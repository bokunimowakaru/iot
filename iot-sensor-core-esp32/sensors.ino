/* extern RTC_DATA_ATTR
RTC_DATA_ATTR char SSID_STA[16] = "";
RTC_DATA_ATTR char PASS_STA[32] = "";
RTC_DATA_ATTR byte PIN_LED		= 2;			// GPIO 2(24番ピン)にLEDを接続
RTC_DATA_ATTR byte PIN_SW		= 0;			// GPIO 0(25番ピン)にスイッチを接続
RTC_DATA_ATTR byte WIFI_AP_MODE	= 1;			// Wi-Fi APモード ※2:STAモード
RTC_DATA_ATTR int  SLEEP_SEC	= 0;			// スリープ間隔
RTC_DATA_ATTR int  TIMEOUT		= 10000;		// タイムアウト 10秒
RTC_DATA_ATTR int  PORT			= 1024; 		// ポート番号
RTC_DATA_ATTR char DEVICE[9]	= "esp32_1,";	// デバイス名(5文字+"_"+番号+",")
RTC_DATA_ATTR int  AmbientChannelId = 0; 		// チャネル名(整数) 0=無効
RTC_DATA_ATTR char AmbientWriteKey[17]="0123456789abcdef";	// ライトキー(16文字)

// デバイス有効化
RTC_DATA_ATTR boolean	LCD_EN=false;
RTC_DATA_ATTR boolean	NTP_EN=false;
RTC_DATA_ATTR boolean	UDP_EN=true;
RTC_DATA_ATTR boolean	TEMP_EN=true;
RTC_DATA_ATTR boolean	HALL_EN=false;
RTC_DATA_ATTR byte		ADC_EN=0;
*/

String sensors_get(){
	boolean csv_b=false;
	String PAYLOAD="";
	if(TEMP_EN){
		int temp = (int)temperatureRead() - 50;
		Serial.print("temperature= ");
		Serial.println(temp);
		if(csv_b) PAYLOAD = PAYLOAD + ", ";
		PAYLOAD = PAYLOAD + String(temp);
		csv_b = true;
	}
	if(HALL_EN){
		int hall=0;
		for(int i=0;i<50;i++) hall += (int)hallRead();
		hall /= 50;
		Serial.print("hall       = ");
		Serial.println(hall);
		if(csv_b) PAYLOAD = PAYLOAD + ", ";
		PAYLOAD = PAYLOAD + String(hall);
		csv_b = true;
	}
	if(ADC_EN){
		mvAnalogIn_init(ADC_EN);
		int adc = (int)mvAnalogIn(ADC_EN);
		Serial.print("adc        = ");
		Serial.println(adc);
		if(csv_b) PAYLOAD = PAYLOAD + ", ";
		PAYLOAD = PAYLOAD + String(adc);
		csv_b = true;
	}
	return PAYLOAD;
}
