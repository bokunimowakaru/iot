/* extern RTC_DATA_ATTR
// ユーザ設定
RTC_DATA_ATTR char SSID_AP[16]="iot-core-esp32";	// 本機のSSID 15文字まで
RTC_DATA_ATTR char PASS_AP[16]="password";			// 本機のPASS 15文字まで
RTC_DATA_ATTR char 		SSID_STA[16] = "";		// STAモードのSSID(お手持ちのAPのSSID)
RTC_DATA_ATTR char 		PASS_STA[32] = "";		// STAモードのPASS(お手持ちのAPのPASS)
RTC_DATA_ATTR byte 		PIN_LED		= 2;		// GPIO 2(24番ピン)にLEDを接続
RTC_DATA_ATTR byte 		PIN_SW		= 0;		// GPIO 0(25番ピン)にスイッチ/PIRを接続
RTC_DATA_ATTR byte 		WIFI_AP_MODE	= 1;	// Wi-Fi APモード ※2:STAモード
RTC_DATA_ATTR uint16_t	SLEEP_SEC	= 0;		// スリープ間隔
RTC_DATA_ATTR uint16_t	SEND_INT_SEC	= 0;	// 送信間隔(非スリープ時)
RTC_DATA_ATTR uint16_t	TIMEOUT		= 10000;	// タイムアウト 10秒
RTC_DATA_ATTR uint16_t	UDP_PORT	= 1024; 	// UDP ポート番号
RTC_DATA_ATTR char		DEVICE[9]	= "esp32_1,";	// デバイス名(5文字+"_"+番号+",")
RTC_DATA_ATTR boolean	MDNS_EN=false;			// MDNS responder
RTC_DATA_ATTR uint16_t	AmbientChannelId = 0; 		// チャネル名(整数) 0=無効
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

void sensors_btnPrev(boolean in){
	sensors_btnPrev_b = in;
}

void sensors_btnPush(boolean in){
	sensors_btnPush_b = in;
}

boolean sensors_btnRead(){
	boolean btn = (boolean)!digitalRead(PIN_SW);
	if( sensors_btnPrev_b != btn){
		sensors_btnPush_b = btn;
		sensors_get();
		return true;
	}
	return false;
}

void sensors_pirPrev(boolean in){
	sensors_pirPrev_b = in;
}

void sensors_pirPush(boolean in){
	sensors_pirPush_b = in;
}

boolean sensors_csv(String &S, boolean csv_b){
	if(csv_b) S += ", ";
	return true;
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
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(hall);
		sensors_S += "磁気";
	}
	if(ADC_EN){
		mvAnalogIn_init(ADC_EN);
		int adc = (int)mvAnalogIn(ADC_EN);
		Serial.print("adc        = ");
		Serial.println(adc);
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
		if(BTN_EN==2){
			if(sensors_btnPrev_b != btn_b){
				if( btn_b ) sensors_sendUdp("Ping");
				else        sensors_sendUdp("Pong");
			}
		}
		sensors_btnPrev_b = btn_b;
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(btn);
		sensors_S += "ボタン";
	}
	return payload;
}

void sensors_sendUdp(String payload){
	WiFiUDP udp;								// UDP通信用のインスタンスを定義
	udp.beginPacket(IP_BC, UDP_PORT);			// UDP送信先を設定
	udp.println(payload);						// センサ値
	udp.endPacket();							// UDP送信の終了(実際に送信する)
	udp.flush();
	udp.stop();
}
