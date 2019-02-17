/* extern RTC_DATA_ATTR
// ユーザ設定
RTC_DATA_ATTR char SSID_AP[16]="iot-core-esp32";	// 本機のSSID 15文字まで
RTC_DATA_ATTR char PASS_AP[16]="password";			// 本機のPASS 15文字まで
RTC_DATA_ATTR char 		SSID_STA[16] = "";		// STAモードのSSID(お手持ちのAPのSSID)
RTC_DATA_ATTR char 		PASS_STA[32] = "";		// STAモードのPASS(お手持ちのAPのPASS)
RTC_DATA_ATTR byte 		PIN_LED		= 2;		// GPIO 2(24番ピン)にLEDを接続
RTC_DATA_ATTR byte 		PIN_SW		= 0;		// GPIO 0(25番ピン)にスイッチを接続
RTC_DATA_ATTR byte 		PIN_PIR		= 27;		// GPIO 27に人感センサを接続
RTC_DATA_ATTR byte 		PIN_LUM		= 35;		// GPIO 35に照度センサを接続
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

*/

boolean sensors_btnPrev_b = false;				// ボタン；前回の値を記録
boolean sensors_btnPush_b = false;				// ボタン；強制押下
boolean sensors_pirPrev_b = false;				// 人感センサ；前回の値を記録
boolean sensors_pirPush_b = false;				// 人感センサ；強制押下
String sensors_S="";							// センサ名

#define sensors_devices_n 10
const char sensors_devices[sensors_devices_n][6]={
	"temp0",	// 0 内蔵温度センサ
	"hall0",	// 1 内蔵ホールセンサ
	"adcnv",	// 2 ADコンバータ
	"btn_s",	// 3 押しボタン
	"pir_s",	// 4 人感センサ
	"illum",	// 5 照度センサ
	"temp.",	// 6 温度センサ
	"humid",	// 7 温湿度センサ
	"envir",	// 8 温湿度＋気圧センサ（温度,湿度,気圧）
	"accem"		// 9 加速度センサ
};
/*
	"rd_sw",	// ドア開閉スイッチ
	"press",	// 気圧センサ
	"e_co2",	// ガスセンサ
	"timer",	// 時刻送信機
	"ir_in",	// 赤外線リモコン信号レシーバ(信号長,16進数データ)
	"ir_rc",	// 赤外線リモコン信号トランスミッタ
	"cam_a",	// カメラHTTPサーバのURI
	"sound",	// オーディオHTTPサーバのURI
	"adash",	// Wi-Fiセンサ
	"atalk",
	"voice",
	"alarm",
*/

void sensors_btnPrev(boolean in){
	sensors_btnPrev_b = in;
}

void sensors_btnPush(boolean in){
	sensors_btnPush_b = in;
}

boolean sensors_btnRead(){
	if(BTN_EN>0){
		boolean btn = (boolean)!digitalRead(PIN_SW);
		if( sensors_btnPrev_b != btn){
			sensors_get();
			return true;
		}
	}
	return false;
}

void sensors_pirPrev(boolean in){
	sensors_pirPrev_b = in;
}

void sensors_pirPush(boolean in){
	sensors_pirPush_b = in;
}

boolean sensors_pirRead(){
	if(PIR_EN){
		boolean pir = (boolean)digitalRead(PIN_PIR);
		if( sensors_pirPrev_b != pir){
			sensors_get();
			return true;
		}
	}
	return false;
}

boolean sensors_csv(String &S, boolean csv_b){
	if(csv_b) S += ", ";
	return true;
}

String sensors_deviceName(int index){
	if(index >= sensors_devices_n || index < 0) return "";
	return String(sensors_devices[index]);
}

String sensors_name(){
	return sensors_S;
}

String sensors_get(){
	boolean csv_b=false;
	String payload="";
	sensors_S="";
	
	if(TEMP_EN){
		int temp = (int)temperatureRead() + (int)TEMP_ADJ - 35;
		Serial.print("temperature= ");
		Serial.println(temp);
		sensors_sendUdp(sensors_devices[0], String(temp));
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(temp);
		sensors_S += "温度(℃)";
	}
	if(HALL_EN){
		int hall=0;
		for(int i=0;i<50;i++) hall += (int)hallRead();
		hall /= 50;
		Serial.print("hall       = ");
		Serial.println(hall);
		sensors_sendUdp(sensors_devices[1], String(hall));
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(hall);
		sensors_S += "磁気";
	}
	if(ADC_EN){
		int adc = (int)mvAnalogIn(ADC_EN);
		Serial.print("adc        = ");
		Serial.println(adc);
		sensors_sendUdp(sensors_devices[2], String(adc));
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(adc);
		sensors_S += "ADC";
	}
	if(BTN_EN>0){
		pinMode(PIN_SW,INPUT_PULLUP);
		int btn = !digitalRead(PIN_SW);		// open=0,HIGH, push=1,LOW
		if( sensors_btnPush_b ) btn =1;
		boolean btn_b = (boolean)btn;
		Serial.print("btn        = ");
		Serial.println(btn);
		if(sensors_btnPrev_b != btn_b || sensors_btnPush_b){
			if(BTN_EN==2){
				if( btn_b ) sensors_sendUdp("Ping");
				else        sensors_sendUdp("Pong");
			}else{
				sensors_sendUdp(sensors_devices[3], String(btn));
			}
		}
		sensors_btnPush_b = false;
		sensors_btnPrev_b = btn_b;
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(btn);
		sensors_S += "ボタン";
	}
	if(PIR_EN){
		int pir = digitalRead(PIN_PIR);
		if( sensors_pirPush_b ) pir =1;
		boolean pir_b = (boolean)pir;
		Serial.print("pir        = ");
		Serial.println(pir);
		if(sensors_pirPrev_b != pir_b || sensors_pirPush_b){
			sensors_sendUdp(sensors_devices[4], String(pir));
		}
		sensors_pirPush_b = false;
		sensors_pirPrev_b = pir_b;
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(pir);
		sensors_S += "人感";
	}
	if(AD_LUM_EN){
		float lum = (float)analogRead(PIN_LUM) / 4096. * 3100 ;  // 直読み値
		lum *= 100. / 33.;                      // 照度(lx)へ変換
		int lum_i = (int)lum;
		Serial.print("illum      = ");
		Serial.println(lum_i);
		sensors_sendUdp(sensors_devices[5], String(lum_i));
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(lum_i);
		sensors_S += "照度(lx)";
	}
	if(AD_TEMP_EN>0){
		float temp = mvAnalogIn(PIN_TEMP);
		if( AD_TEMP_EN == 1){		// 1:LM61, 2:MCP9700
			// V = 600 + 10*temp -> (temp-600)/10
			temp /= 10.;                            // 温度(相対値)へ変換
			temp += (float)TEMP_ADJ - 60.;             // 温度(相対値)へ変換
		}else{
			// V = 500 + 10*temp -> (temp-500)/10
			temp /= 10.;                            // 温度(相対値)へ変換
			temp += (float)TEMP_ADJ - 50.;             // 温度(相対値)へ変換
		}
		String temp_S = String((int)temp) + "." + dtoStrf(temp,1);
		Serial.print("temp.      = ");
		Serial.println(temp_S);
		sensors_sendUdp(sensors_devices[6], temp_S);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(temp_S);
		sensors_S += "温度(℃)";
	}
	
	sensors_sendUdp(DEVICE, payload);
	return payload;
}

String sensors_sendUdp(String payload){
	WiFiUDP udp;								// UDP通信用のインスタンスを定義
	udp.beginPacket(IP_BC, UDP_PORT);			// UDP送信先を設定
	udp.println(payload);						// センサ値
	udp.endPacket();							// UDP送信の終了(実際に送信する)
	udp.flush();
	udp.stop();
	return payload;
}

String sensors_sendUdp(const char *device, String payload){		// main/sendUdp
	if(UDP_PORT > 0 && payload.length() > 0){
		String S = String(device) + "_" + String(DEVICE_NUM) + "," + payload;
		WiFiUDP udp;								// UDP通信用のインスタンスを定義
		udp.beginPacket(IP_BC, UDP_PORT);			// UDP送信先を設定
		udp.println(S);								// センサ値
		udp.endPacket();							// UDP送信の終了(実際に送信する)
		udp.flush();
		udp.stop();
		Serial.println("udp://" + html_ipAdrToString(IP_BC) +":" + String(UDP_PORT) + " \"" + S + "\"");
		delay(10);
		return S;
	}
	return "";
}
