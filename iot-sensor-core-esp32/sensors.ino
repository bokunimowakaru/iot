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

const byte	sensors_adc_pin[5]={0,32,33,34,35};

#define sensors_devices_n 10
boolean sensors_devices_inited[sensors_devices_n];
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


const String sensors_PINOUT_S[38] = {
	"GND","3V3","EN","SVP","SVN","IO34","IO35","IO32","IO33","IO25","IO26","IO27","IO14","IO12","GND","IO13","SD2","SD3","CMD",
	"CLK","SDD","SD1","IO15","IO2","IO0","IO4","IO16","IO17","IO5","IO18","IO19","NC","IO21","RXD0","TXD0","IO22","IO23","GND"};

String sensors_PIN_ASSIGNED_S[38] = {
	"電池(-)","電池(+)","リセットボタン","SVP","SVN","IO34","IO35","IO32","IO33","IO25","IO26","IO27","IO14","IO12","GND","IO13","","","",
	"","","","IO15","IO2","ボタン","IO4","IO16","IO17","IO5","IO18","IO19","","IO21","USBシリアル(TxD)","USBシリアル(RxD)","IO22","IO23","GND"};
	
	/* Null = ピンの無いもの、PINOUTと同値 = ピンアサインの無いもの */

const byte sensors_adcPins(int i){
	if( i<0 || i>4 ) return 0;
	return sensors_adc_pin[i];
}

const String sensors_pinout_S(int i){
	if( i<0 || i>37 ) return "";
	return sensors_PINOUT_S[i];
}

String sensors_pin_assigned_S(int i){
	if( i<0 || i>37 ) return "";
	return sensors_PIN_ASSIGNED_S[i];
}

boolean sensors_pin_set(String pin, String name){
	for(int i=0; i< 38;i++){
		if( pin.equals(sensors_PINOUT_S[i]) ){
			if( sensors_PIN_ASSIGNED_S[i].equals(sensors_PINOUT_S[i]) ){
				sensors_PIN_ASSIGNED_S[i] = name;
				return true;
			}
			if( sensors_PIN_ASSIGNED_S[i].equals(name) ){
				return true;
			}
			return false;
		}
	}
	return false;
}

boolean sensors_pin_reset(String pin, String name){
	for(int i=0; i< 38;i++){
		if( pin.equals(sensors_PINOUT_S[i]) ){
			if( sensors_PIN_ASSIGNED_S[i].equals(name) ){
				sensors_PIN_ASSIGNED_S[i] = sensors_PINOUT_S[i];
				return true;
			}
			return false;
		}
	}
	return false;
}

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

void sensors_init(){
	for(int i=0;i<sensors_devices_n;i++)sensors_devices_inited[i]=false;
//	if(LCD_EN)			sensors_init_LCD();
	if(TEMP_EN)			sensors_init_TEMP(1);
	if(HALL_EN)			sensors_init_HALL(1);
	if(ADC_EN)			sensors_init_ADC(ADC_EN);
	if(BTN_EN)			sensors_init_BTN(BTN_EN);
	if(PIR_EN)			sensors_init_PIR(1);
	if(AD_LUM_EN)		sensors_init_AD_LUM(1);
	if(AD_TEMP_EN)		sensors_init_AD_TEMP(AD_TEMP_EN);
	if(I2C_HUM_EN)		sensors_init_I2C_HUM(I2C_HUM_EN);
	if(I2C_ENV_EN)		sensors_init_I2C_ENV(I2C_ENV_EN);
	if(I2C_ACCUM_EN)	sensors_init_I2C_ACCUM(1);
}

boolean sensors_init_LCD(int enable){
	if( enable > 0 ) LCD_EN=true;
	else LCD_EN=false;
	return true;
}

boolean sensors_init_TEMP(int enable){
	if( enable > 0 ) TEMP_EN=true;
	else TEMP_EN=false;
	return true;
}

boolean sensors_init_HALL(int enable){
	if( enable > 0 ) HALL_EN=true;
	else HALL_EN=false;
	return true;
}

boolean sensors_init_ADC(int pin){
	boolean ret = true;		// ピン干渉なし
	int i;
	for(i=1;i<5;i++){
		if(pin == sensors_adc_pin[i]){
			if(sensors_pin_set("IO" + String(pin),"アナログ_IN")){
				ADC_EN=pin;
				mvAnalogIn_init(ADC_EN);
			}else{
				sensors_pin_reset("IO" + String(sensors_adc_pin[i]),"アナログ_IN");
				ret = false;		// ピン干渉
			}
		}else sensors_pin_reset("IO" + String(sensors_adc_pin[i]),"アナログ_IN");
	}
	if( i==5 ) ADC_EN=0;		// pin ==0も含む
	return ret;
}

boolean sensors_init_BTN(int mode){
	// このピンの割り当て変更はしない
	if( mode >= 0 && mode <= 2) BTN_EN=mode;
	else BTN_EN=1;
	return true;
}

boolean sensors_init_PIR(int enable){
	boolean ret = true;		// ピン干渉なし
	if( enable > 0 ){
		if(	sensors_pin_set("IO14","人感_GND") &&
			sensors_pin_set("IO" + String(PIN_PIR),"人感_IN") &&
			sensors_pin_set("IO26","人感_VDD")
		){	pinMode(14,OUTPUT);	digitalWrite(14,LOW);
			pinMode(PIN_PIR,INPUT);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			PIR_EN=true;
		}else{
			ret = false;		// ピン干渉
			PIR_EN=false;
		}
	}else PIR_EN=false;
	
	if(!PIR_EN){
		sensors_pin_reset("IO14","人感_GND");
		sensors_pin_reset("IO" + String(PIN_PIR),"人感_IN");
		sensors_pin_reset("IO26","人感_VIN");
	}
	return ret;
}

boolean sensors_init_AD_LUM(int enable){
	boolean ret = true;		// ピン干渉なし
	if( enable > 0 ){
		if(	sensors_pin_set("IO32","照度_GND") &&
			sensors_pin_set("IO" + String(PIN_LUM),"照度_IN") &&
			sensors_pin_set("IO25","照度_+V")
		){	pinMode(32,OUTPUT);	digitalWrite(32,LOW);
			pinMode(PIN_PIR,INPUT_PULLDOWN);
			pinMode(25,OUTPUT);	digitalWrite(25,HIGH);
			AD_LUM_EN=true;
		}else{
			ret = false;		// ピン干渉
			AD_LUM_EN=false;
		}
	}else AD_LUM_EN=false;
	
	if(!AD_LUM_EN){
		sensors_pin_reset("IO32","照度_GND");
		sensors_pin_reset("IO" + String(PIN_LUM),"照度_IN");
		sensors_pin_reset("IO25","照度_+V");
	}
	return ret;
}

boolean sensors_init_AD_TEMP(int mode){
	boolean ret = true;		// ピン干渉なし
	if( mode >= 1 && mode <= 2 ){
		if(	sensors_pin_set("IO32","温度_GND") &&
			sensors_pin_set("IO" + String(PIN_TEMP),"温度_IN") &&
			sensors_pin_set("IO25","温度_+V")
		){	pinMode(32,OUTPUT);	digitalWrite(32,LOW);
			pinMode(PIN_TEMP,INPUT);
			pinMode(25,OUTPUT);	digitalWrite(25,HIGH);
			AD_TEMP_EN=mode;
		}else{
			ret = false;		// ピン干渉
			AD_TEMP_EN=0;
		}
	}
	if(!AD_TEMP_EN){
		sensors_pin_reset("IO32","温度_GND");
		sensors_pin_reset("IO" + String(PIN_TEMP),"温度_IN");
		sensors_pin_reset("IO25","温度_+V");
		AD_TEMP_EN=0;
	}
	return ret;
}

boolean sensors_init_I2C_HUM(int mode){
	boolean ret = true;		// ピン干渉なし
	if( mode >= 1 && mode <=2 ){
		if( mode == 1){
			if( sensors_pin_set("IO13","SHT31_ADR") &&
				sensors_pin_set("IO12","SHT31_I2C_SCL") &&
				sensors_pin_set("IO14","SHT31_I2C_SDA") &&
				sensors_pin_set("IO27","SHT31_+V")
			){	pinMode(13,OUTPUT);	digitalWrite(13,HIGH);
				pinMode(27,OUTPUT);	digitalWrite(27,HIGH);
				i2c_sht31_Setup(14,12);
				I2C_HUM_EN=1;
			}else{
				ret = true;
				I2C_HUM_EN=0;
			}
		}
		if( mode == 2){
			if( sensors_pin_set("IO14","Si7021_GND") &&
				sensors_pin_set("IO12","Si7021_I2C_SCL") &&
				sensors_pin_set("IO13","Si7021_I2C_SDA") &&
				sensors_pin_set("IO27","Si7021_+V")
			){	pinMode(14,OUTPUT);	digitalWrite(14,LOW);
				pinMode(27,OUTPUT);	digitalWrite(27,HIGH);
				i2c_sht31_Setup(13,12);
				I2C_HUM_EN=2;
			}else{
				ret = true;
				I2C_HUM_EN=0;
			}
		}
	}
	if(I2C_HUM_EN != 1){
		sensors_pin_reset("IO13","SHT31_ADR");
		sensors_pin_reset("IO12","SHT31_I2C_SCL");
		sensors_pin_reset("IO14","SHT31_I2C_SDA");
		sensors_pin_reset("IO27","SHT31_+V");
	}
	if(I2C_HUM_EN != 2){
		sensors_pin_set("IO14","Si7021_GND");
		sensors_pin_set("IO12","Si7021_I2C_SCL");
		sensors_pin_set("IO13","Si7021_I2C_SDA");
		sensors_pin_set("IO27","Si7021_+V");
	}
	return ret;
}

boolean sensors_init_I2C_ENV(int mode){
	boolean ret = true;		// ピン干渉なし
	return ret;
}
boolean sensors_init_I2C_ACCUM(int enable){
	boolean ret = true;		// ピン干渉なし
	return ret;
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
		String temp_S = dtoStrf(temp,1);
		Serial.print("temp.      = ");
		Serial.println(temp_S);
		sensors_sendUdp(sensors_devices[6], temp_S);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(temp_S);
		sensors_S += "温度(℃)";
	}
	if(I2C_HUM_EN>0){		// 1:SHT31, 2:Si7021
		float temp = -999, hum = -999;
		if( I2C_HUM_EN == 1){
			temp = i2c_sht31_getTemp();
			hum = i2c_sht31_getHum();
		}
		if( I2C_HUM_EN == 2){
			temp = i2c_si7021_getTemp();
			hum = i2c_si7021_getHum();
		}
		String hum_S = dtoStrf(temp,1) + ", " + dtoStrf(hum,0);
		Serial.print("humid      = ");
		Serial.println(hum_S);
		if(temp >= -100 && hum >= 0 ){
			sensors_sendUdp(sensors_devices[7], hum_S);
		}else hum_S = "0, 0";
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(hum_S);
		sensors_S += "温度(℃)";
		sensors_csv(sensors_S,csv_b);
		sensors_S += "湿度(％)";
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
