/*******************************************************************************
IoT Sensor Core for ESP32

										   Copyright (c) 2019 Wataru KUNINO
*******************************************************************************/
#include <WiFi.h>								// ESP32用WiFiライブラリ
#include <WiFiUdp.h>							// UDP通信を行うライブラリ
#include <ESPmDNS.h>
#include "Ambient.h"							// Ambient接続用 ライブラリ

// ユーザ設定
RTC_DATA_ATTR char SSID_AP[16]="iot-core-esp32";	// 本機のSSID 15文字まで
RTC_DATA_ATTR char PASS_AP[16]="password";			// 本機のPASS 15文字まで
RTC_DATA_ATTR char 		SSID_STA[16] = "";		// STAモードのSSID(お手持ちのAPのSSID)
RTC_DATA_ATTR char 		PASS_STA[32] = "";		// STAモードのPASS(お手持ちのAPのPASS)
RTC_DATA_ATTR byte 		PIN_LED		= 2;		// GPIO 2(24番ピン)にLEDを接続
RTC_DATA_ATTR byte 		PIN_SW		= 0;		// GPIO 0(25番ピン)にスイッチを接続
RTC_DATA_ATTR byte 		PIN_PIR		= 27;		// GPIO 27に人感センサを接続
RTC_DATA_ATTR byte 		PIN_LUM		= 33;		// GPIO 33に照度センサを接続
RTC_DATA_ATTR byte 		PIN_TEMP	= 33;		// GPIO 33に温度センサを接続
RTC_DATA_ATTR byte 		WIFI_AP_MODE	= 1;	// Wi-Fi APモード ※2:STAモード
RTC_DATA_ATTR uint16_t	SLEEP_SEC	= 0;		// スリープ間隔
RTC_DATA_ATTR uint16_t	SEND_INT_SEC	= 60;	// 自動送信間隔(非スリープ時)
RTC_DATA_ATTR uint16_t	TIMEOUT		= 10000;	// タイムアウト 10秒
RTC_DATA_ATTR uint16_t	UDP_PORT	= 1024; 	// UDP ポート番号
RTC_DATA_ATTR char		DEVICE[6]	= "esp32";	// デバイス名(5文字)
RTC_DATA_ATTR char 		DEVICE_NUM	= '2';		// デバイス番号
RTC_DATA_ATTR boolean	MDNS_EN=false;			// MDNS responder
RTC_DATA_ATTR int		AmbientChannelId = 0; 	// チャネル名(整数) 0=無効
RTC_DATA_ATTR char		AmbientWriteKey[17]="0123456789abcdef";	// ライトキー(16文字)

// デバイス有効化
RTC_DATA_ATTR boolean	LCD_EN=false;
RTC_DATA_ATTR boolean	NTP_EN=false;
RTC_DATA_ATTR boolean	TEMP_EN=true;
RTC_DATA_ATTR int8_t	TEMP_ADJ=0;
RTC_DATA_ATTR boolean	HALL_EN=false;
RTC_DATA_ATTR byte		ADC_EN=0;
RTC_DATA_ATTR byte		BTN_EN=0;				// 1:ON(L) 2:PingPong
RTC_DATA_ATTR boolean	PIR_EN=false;
RTC_DATA_ATTR boolean	AD_LUM_EN=false;
RTC_DATA_ATTR byte		AD_TEMP_EN=0;			// 1:LM61, 2:MCP9700
RTC_DATA_ATTR byte		I2C_HUM_EN=0;			// 1:SHT31, 2:Si7021
RTC_DATA_ATTR byte		I2C_ENV_EN=0;			// 1:BME280, 2:BMP280
RTC_DATA_ATTR boolean	I2C_ACCUM_EN=false;

IPAddress IP;									// IPアドレス
IPAddress IP_BC;								// ブロードキャストIPアドレス
Ambient ambient;								// クラウドサーバ Ambient用
WiFiClient ambClient;							// Ambient接続用のTCPクライアント

unsigned long TIME=0;							// 1970年からmillis()＝0までの秒数
unsigned long TIME_NEXT=0;						// 次回の送信時刻(ミリ秒)
boolean TIME_NEXT_b=false;						// 桁あふれフラグ

boolean setupWifiAp(){
	delay(1000);								// 切換え・設定待ち時間
	WiFi.softAPConfig(
		IPAddress(192,168,254,1), 				// AP側の固定IPアドレス
		IPAddress(192,168,254,1), 				// 本機のゲートウェイアドレス
		IPAddress(255,255,255,0)				// ネットマスク
	);
	WiFi.softAP(SSID_AP,PASS_AP);				// ソフトウェアAPの起動

	Serial.print("SoftAP  IP = "); Serial.println(WiFi.softAPIP());
	Serial.println("Software AP started");
	return true;
}

boolean setupWifiSta(){
	unsigned long start_ms=millis();			// 初期化開始時のタイマー値を保存
	WiFi.begin(SSID_STA,PASS_STA);				// 無線LANアクセスポイントへ接続
	while(WiFi.status()!=WL_CONNECTED){ 		// 接続に成功するまで待つ
		delay(500); 							// 待ち時間処理
		digitalWrite(PIN_LED,!digitalRead(PIN_LED));	// LEDの点滅
		Serial.print(".");
		if(millis()-start_ms>TIMEOUT){			// 待ち時間後の処理
			WiFi.disconnect();					// WiFiアクセスポイントを切断する
			Serial.println();					// 改行をシリアル出力
			Serial.println("No Internet AP");	// 接続が出来なかったときの表示
			return false;
		}
	}
	Serial.println();							// 改行をシリアル出力
	Serial.print("Station IP = ");
	Serial.println(WiFi.localIP() );			// IPアドレスをシリアル表示
	Serial.print("      Mask = ");
	Serial.println(WiFi.subnetMask());			// ネットマスクをシリアル表示
	Serial.print("   Gateway = ");
	Serial.println(WiFi.gatewayIP());			// ゲートウェイをシリアル表示
	Serial.println("Station started");
	return true;
}

String sendUdp(String &payload){
	if(UDP_PORT > 0 && payload.length() > 0){
		String S = String(DEVICE) + "_" + String(DEVICE_NUM) + "," + payload;
		WiFiUDP udp;								// UDP通信用のインスタンスを定義
		udp.beginPacket(IP_BC, UDP_PORT);			// UDP送信先を設定
		DEVICE[5]='\0';								// 終端
		udp.println(S);						 		// 送信
		udp.endPacket();							// UDP送信の終了(実際に送信する)
		udp.flush();
		udp.stop();
		Serial.println("udp://" + html_ipAdrToString(IP_BC) +":" + String(UDP_PORT) + " \"" + S + "\"");
		delay(10);
		return S;
	} else return "";
}

boolean sentToAmbient(String &payload){
	if(AmbientChannelId == 0) return false;
	if(WiFi.status() != WL_CONNECTED) return false;
	if(payload.length() == 0) return false;

	ambient.begin(AmbientChannelId, AmbientWriteKey, &ambClient);
	int Sp=0;
	char s[16];
	for(int num = 1; num <= 8; num++){
		float val = payload.substring(Sp).toFloat();
		Serial.println("http://ambidata.io/ POST {\"d"
			+ String(num)
			+ "\":"
			+ String(val)
			+ "}"
		);
		dtostrf(val,-15,3,s);
		ambient.set(num,s);
		Sp = payload.indexOf(",", Sp) + 1;
		if( Sp <= 0 ) break;
		if( Sp >= payload.length() ) break;
	}
	boolean ret = ambient.send();
	if( ambClient.available() ) ambClient.stop();
	return ret;
}

String sendSensorValues(){
	Serial.println("Start: send Sensor Values");
	String payload = String(sensors_get());
	if( payload.length() ){
		Serial.println("Done: send UDP to LAN");
		if( sentToAmbient(payload) ){
			Serial.println("Done: send to Ambient");
		}
	}
	return payload;
}

void setup(){
	pinMode(PIN_LED,OUTPUT);					// LEDを接続したポートを出力に
	sensors_init();
	if(LCD_EN)lcdSetup();						// 液晶の初期化
	Serial.begin(115200);
	Serial.println("--------");
	int wake = TimerWakeUp_init();
	if(BTN_EN > 0){
		pinMode(PIN_SW,INPUT_PULLUP);
		if(wake == 1 || wake == 2) sensors_btnPush(true);
		if(wake == 3 || wake == 4){
			if(digitalRead(PIN_SW)) sleep();
		}
	}
	if(PIR_EN){
		pinMode(PIN_PIR,INPUT_PULLUP);
		pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
		pinMode(14,OUTPUT);	digitalWrite(14,LOW);
		if(wake == 1 || wake == 2) sensors_pirPush(true);
		if(wake == 3 || wake == 4){
			if(!digitalRead(PIN_PIR)) sleep();
		}
	}
	if(TimerWakeUp_init() > 0){
	}
	
	Serial.println("-------- IoT Sensor Core ESP32 by Wataru KUNINO --------");
	Serial.print("Wi-Fi Mode = ");
	if(WIFI_AP_MODE>=0 && WIFI_AP_MODE<=3){
		char mode_s[4][7]={"OFF","AP","STA","AP+STA"};
		Serial.println( mode_s[WIFI_AP_MODE] );
	}else Serial.println( WIFI_AP_MODE );
	Serial.println("SSID_AP    = " + String(SSID_AP) );
	Serial.println("PASS_AP    = " + String(PASS_AP) );
	if(strlen(SSID_STA)>0)Serial.println("SSID_STA   = " + String(SSID_STA) );
	if(strlen(PASS_STA)>0)Serial.println("PASS_STA   = ********");
	
	delay(10);									// ESP32に必要な待ち時間
	switch(WIFI_AP_MODE){
		case 1:	// WIFI_AP
			WiFi.mode(WIFI_AP); 				// 無線LANを[AP]モードに設定
			setupWifiAp();
			IP = WiFi.softAPIP();
			IP_BC = (uint32_t)IP | IPAddress(0,0,0,255);
			break;
		case 2:	// WIFI_STA
			WiFi.mode(WIFI_STA);				// 無線LANを[STA]モードに設定
			setupWifiSta();
			IP = WiFi.localIP();
			IP_BC = (uint32_t)IP | ~(uint32_t)(WiFi.subnetMask());
			break;
		case 3:	// WIFI_AP_STA
			WiFi.mode(WIFI_AP_STA);				// 無線LANを[AP+STA]モードに設定
			setupWifiAp();
			setupWifiSta();
			IP = WiFi.softAPIP();
			IP_BC = (uint32_t)(WiFi.localIP()) | IPAddress(0,0,0,255);
			break;
		default: // WIFI_OFF
			WiFi.mode(WIFI_OFF);
			IP = IPAddress(0,0,0,0);
			IP_BC = IPAddress(255,255,255,255);
	}
	if( (uint32_t)IP > 0 ) digitalWrite(PIN_LED,HIGH);
	else{
		digitalWrite(PIN_LED,LOW);
		Serial.println("Wi-Fi Mode = OFF");
		TimerWakeUp_setSleepTime(SLEEP_SEC);
		TimerWakeUp_sleep();
	}

	if(WiFi.status() == WL_CONNECTED){			// 接続に成功した時
		if(NTP_EN){
			Serial.println("NTP client started");
			TIME=getNtp();						// NTP時刻を取得
			TIME-=millis()/1000;				// カウント済み内部タイマー事前考慮
		}
	}
	
	// HTTP サーバ
	if( (WIFI_AP_MODE & 1) == 1 ){				// WiFi_AP 動作時
		MDNS_EN=MDNS.begin("iot");
		if(MDNS_EN) Serial.println("MDNS responder started");
	}
	html_init(IP,"iot");
	Serial.print("WebServ IP = ");
	Serial.println( IP );
	Serial.print("     BC IP = ");
	Serial.println( IP_BC );
	if(MDNS_EN)Serial.println(" URL(mDNS) = http://iot.local/");
	Serial.print("   URL(IP) = http://");
	Serial.print(IP);
	Serial.println("/");
	sendSensorValues();
	TIME_NEXT = millis() + (unsigned long)SEND_INT_SEC * 1000;
}

void loop(){
	html_handleClient();
	sensors_btnRead();
	sensors_pirRead();
	sleep();
	
	unsigned long time=millis();            // ミリ秒の取得
	if(time<100){
		TIME_NEXT_b = false;
		if(NTP_EN){
			Serial.println("NTP client started");
			TIME=getNtp();					// NTP時刻を取得
			TIME-=millis()/1000;			// カウント済み内部タイマー事前考慮
		}
		while( millis() < 100 ) delay(10);	// 待ち時間処理(最大100ms)
	}
	if(time > TIME_NEXT && !TIME_NEXT_b){
		Serial.println("MCU Clock_s= " + String(time/1000));
		sendSensorValues();
		if(SEND_INT_SEC){
			TIME_NEXT = millis() + (unsigned long)SEND_INT_SEC * 1000;
			if( TIME_NEXT < (unsigned long)SEND_INT_SEC * 1000 ) TIME_NEXT_b = true;
		}else{
			TIME_NEXT = millis() + 5000ul;
			if( TIME_NEXT < 5000ul ) TIME_NEXT_b = true;
		}
	}
}

void sleep(){
	if( ((WIFI_AP_MODE & 2) == 2) && (SLEEP_SEC > 0) ){		// WiFi_STA 動作時
		if( millis() < TIMEOUT ) return;
		digitalWrite(PIN_LED,LOW);
		if(BTN_EN>0){
			pinMode(PIN_SW,INPUT_PULLUP);
			while(!digitalRead(PIN_SW)){
				digitalWrite(PIN_LED,!digitalRead(PIN_LED));
				delay(50);
			}
			digitalWrite(PIN_LED,LOW);
			TimerWakeUp_setExternalInput((gpio_num_t)PIN_SW, LOW);
		}
		if(PIR_EN){
			pinMode(14,OUTPUT);	digitalWrite(14,LOW);
			pinMode(PIN_PIR,INPUT);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			while(digitalRead(PIN_PIR)){
				digitalWrite(PIN_LED,!digitalRead(PIN_LED));
				delay(50);
			}
			digitalWrite(PIN_LED,LOW);
			TimerWakeUp_setExternalInput((gpio_num_t)PIN_PIR, HIGH);
		}
		TimerWakeUp_setSleepTime(SLEEP_SEC);
		TimerWakeUp_sleep();
	}
	return;
}
