// extern RTC_DATA_ATTR

boolean sensors_WireBegin = false;				// Wire.beginの実行有無
boolean sensors_btnPrev_b = false;				// ボタン；前回の値を記録
boolean sensors_btnPush_b = false;				// ボタン；強制押下
boolean sensors_pirPrev_b = false;				// 人感センサ；前回の値を記録
boolean sensors_pirPush_b = false;				// 人感センサ；強制押下
String sensors_S="";							// センサ名

const byte	sensors_adc_pin[5]={0,32,33,34,35};

#define sensors_devices_n 11
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
	"press",	// 8 気圧センサ（温度,気圧）
	"envir",	// 9 温湿度＋気圧センサ（温度,湿度,気圧）
	"accem"		// 10 加速度センサ
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

#define sensors_BOARD_TYPES_NUM 3

String sensors_PINOUT_S[38];
int sensors_PINOUT_PINS = 38;
int sensors_PINOUT_PINS_LOW = 19;

const String sensors_PINOUT_S_AE_ESP[38] = {
	"GND","3V3","EN","SVP","SVN","IO34","IO35","IO32","IO33","IO25","IO26","IO27","IO14","IO12","GND","IO13","SD2","SD3","CMD",
	"CLK","SD0","SD1","IO15","IO2","IO0","IO4","IO16","IO17","IO5","IO18","IO19","NC","IO21","RXD0","TXD0","IO22","IO23","GND"};
const String sensors_PINOUT_S_DevKitC[38] = {
	"3V3","EN","SVP","SVN","IO34","IO35","IO32","IO33","IO25","IO26","IO27","IO14","IO12","GND","IO13","SD2","SD3","CMD","5V",
	"CLK","SD0","SD1","IO15","IO2","IO0","IO4","IO16","IO17","IO5","IO18","IO19","GND","IO21","RXD0","TXD0","IO22","IO23","GND"};
const String sensors_PINOUT_S_TTGO_Koala[36] = {
	"3V3","EN","SVP","SVN","IO32","IO33","IO34","IO35","IO25","IO26","IO27","IO14","IO12","IO13","5V","BAT",
	"IO15","IO2","GND","IO0","IO4","IO16","IO17","3V3","IO5","IO18","IO23","IO19","GND","GND","IO21","IO22","3V3","RXD0","TXD0","GND"};

String sensors_PIN_ASSIGNED_S[38];

/*
DoIt	DevC	AE-ESP	TTGO	メモ	TTGO以外								TTGO_LCD
IO36 i	IO36 i	IO36 i	IO36i
IO39 i	IO39 i	IO39 i	IO39i
IO34 i	IO34 i	IO34 i	IO32★	ADC
IO35 i	IO35 i	IO35 i	IO33★	ADC
IO32	IO32	IO32	IO34 i	ADC				LUM/-
IO33	IO33	IO33	IO35 i	ADC				LUM/O
IO25	IO25	IO25	IO25	共通	PIR/+	LUM/+			BME/+
IO26	IO26	IO26	IO26	共通	PIR/O	SHT/+	Si/+	BME/-	AM2320/+	LCD/+	
IO27	IO27	IO27	IO27	共通	PIR/-	SHT/D	Si/-	BME/C	AM2320/D	LCD/R
IO14	IO14	IO14	IO14	共通	IR/+	SHT/C	Si/C	BME/D	AM2320/-	LCD/C
IO12	IO12	IO12	IO12	PDown★			SHT/A	Si/D	BME/A	AM2320/C	LCD/D
IO13	GND		GND		IO13	GND				SHT/-			BME/0				LCD/-
GND		IO13	IO13	5V
--------------------------------------
IO23	IO23	IO23
IO22	IO22	IO22
TXD		TXD		TXD
RXD		RXD		RXD
IO21	IO21	IO21
		GND		NC
IO19	IO19	IO19			LCD/+
IO18	IO18	IO18			LCD/R
IO5		IO5		IO5		PUp		LCD/C
IO17	IO17	IO17			LCD/D
IO16	IO16	IO16			LCD/-
IO4		IO4		IO4
		IO0		IO0				BTN
IO2		IO2		IO2		PDown	LED		IR_OUT
IO15	IO15	IO15	PUp
GND		
3V3		
*/

/*	専用ピン
	IO0			|Booting Mode	|Default:Pull-up	|0:Download Boot, 1:SPI Boot 
	IO2			|Booting Mode	|Default:Pull-down	// Hレベルだとファーム書き換え不可
	IO5			|Timing SDIO Slv|Default:Pull-up	|0:Falling-edge Output, 1:Rising-edge
	IO12(MTDI)	|VDD_SDIO		|Default:Pull-down	|0:3.3V, 1:1.8V
	IO15(MTDO)	|Debugging Log	|Default:Pull-up	|0:U0TXD Silent, 1:U0TXD Active
	
	VDD_SDIO works as the power supply for the related IO, and also for an external device.
	When the VDD_SDIO outputs 1.8 V, the value of GPIO12 should be set to 1
	When the VDD_SDIO outputs 3.3 V, the value of GPIO12 is 0 (default)
*/

/*	IO20 IO24 IO28 IO29 IO30 IO31
     @note There are more enumerations like that
     up to GPIO39, excluding GPIO20, GPIO24 and GPIO28..31.
*/
/*	IO34 IO35 IO36 IO37 IO38 IO39
     @note GPIO34..39 are input mode only. 
*/

const char *sensors_boardName(int i){
	switch(i){
		case 0:	return "ESP32-WROOM-32";
		case 1:	return "DevKitC";
		case 2:	return "TTGO T-Koala";
		default:break;
	}
	return "AE-ESP-WROOM-32";
}

int sensors_board_types_num(){
	return sensors_BOARD_TYPES_NUM;
}

const byte sensors_adcPins(int i){
	if( i<0 || i>4 ) return 0;
	return sensors_adc_pin[i];
}

String sensors_pinout_S(int i){
	if( i<0 || i>37 ) return "";
	return sensors_PINOUT_S[i];
}

int sensors_pinout_pins(){
	return sensors_PINOUT_PINS;
}

int sensors_pinout_pins_low(){
	return sensors_PINOUT_PINS_LOW;
}

String sensors_pin_assigned_S(int i){
	if( i<0 || i>37 ) return "";
	return sensors_PIN_ASSIGNED_S[i];
}

boolean sensors_pin_set(String pin, String name){
	for(int i=0; i< sensors_PINOUT_PINS;i++){
		if( pin.equals(sensors_PINOUT_S[i]) ){
			if( sensors_PIN_ASSIGNED_S[i].equals(sensors_PINOUT_S[i]) ){
				sensors_PIN_ASSIGNED_S[i] = name;
				return true;
			}
			if( sensors_PIN_ASSIGNED_S[i].equals(name) ){
				return true;
			}
			Serial.print("ERROR:sensors_pin_set, " + String(sensors_PIN_ASSIGNED_S[i]) + " : " + name);
			return false;
		}
	}
	Serial.print("ERROR:no sensors_pin_set, " + name);
	return false;
}

boolean sensors_pin_reset(String pin, String name){
	for(int i=0; i< sensors_PINOUT_PINS;i++){
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

boolean sensors_wireBegin(){
	return sensors_WireBegin;
}

void sensors_btnPrev(boolean in){
	sensors_btnPrev_b = in;
}

void sensors_btnPush(boolean in){
	sensors_btnPush_b = in;
}

boolean sensors_btnRead(const String &S = "");
boolean sensors_btnRead(const String &S){
	if(BTN_EN>0){
		boolean btn = (boolean)!digitalRead(PIN_SW);
		if( sensors_btnPrev_b != btn){
			if(S.length()>0) Serial.println(S);
			sensors_get();
			for(int i=0;i<10;i++)delay(1);	// 待ち時間処理
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

boolean sensors_pirRead(const String &S){
	if(PIR_EN){
		boolean pir = (boolean)digitalRead(PIN_PIR);
		if( sensors_pirPrev_b != pir){
			if(S.length()>0) Serial.println(S);
			sensors_get();
			for(int i=0;i<10;i++)delay(1);	// 待ち時間処理
			return true;
		}
	}
	return false;
}

boolean sensors_pirRead(){
	return sensors_pirRead("");
}

#define sensor_IR_DATA_LEN_MAX 16		// リモコンコードのデータ長(byte)
byte sensor_ir_data8 = 0x00;

byte sensors_ir_data(){
	return sensor_ir_data8;
}

boolean sensors_irRead(boolean noUdp, const String &SP){
	if( !IR_IN_EN) return false;
	boolean ir = (boolean)digitalRead(PIN_IR_IN);
	if( ir ) return false;
	
	byte data[sensor_IR_DATA_LEN_MAX];
	int len = ir_read(data, sensor_IR_DATA_LEN_MAX, IR_IN_EN);
	int len8 = len / 8;
	sensor_ir_data8 = data[len8 - 1];
	if(len%8) len8++;
	if(len8 < 2) return false;
	if(SP.length()>0) Serial.println(SP);
	String S = String(len);
	for(int i=0; i < len8; i++){
		S += ",";
		S += String(data[i]>>4,HEX);
		S += String(data[i]&15,HEX);
	}
	Serial.println("ir_in      = " + S);
	if (!noUdp) sensors_sendUdp("ir_in", S);
	return true;
}

boolean sensors_irRead(const String &S){
	return sensors_irRead(false, S);
}

boolean sensors_irRead(boolean noUdp = false);

boolean sensors_irRead(boolean noUdp){
	return sensors_irRead(noUdp);
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
	sensors_PINOUT_PINS = 38;
	switch(BOARD_TYPE){
		case 0:	sensors_PINOUT_PINS = 38;
				sensors_PINOUT_PINS_LOW = 19;
				break;
		case 1:	sensors_PINOUT_PINS = 38;
				sensors_PINOUT_PINS_LOW = 19;
				break;
		case 2:	sensors_PINOUT_PINS = 36;	// 16 pin + 20 pin
				sensors_PINOUT_PINS_LOW = 16;
				break;
		default:sensors_PINOUT_PINS = 38;
				sensors_PINOUT_PINS_LOW = 19;
	}
	for(int i=0;i<sensors_PINOUT_PINS;i++){
		switch(BOARD_TYPE){
			case 0:	sensors_PINOUT_S[i] = sensors_PINOUT_S_AE_ESP[i];
					break;
			case 1:	sensors_PINOUT_S[i] = sensors_PINOUT_S_DevKitC[i];
					break;
			case 2:	sensors_PINOUT_S[i] = sensors_PINOUT_S_TTGO_Koala[i];
					break;
			default:sensors_PINOUT_S[i] = sensors_PINOUT_S_AE_ESP[i];
		}
		sensors_PIN_ASSIGNED_S[i]=sensors_PINOUT_S[i];
	}
	sensors_pin_set("TXD0", "USBシリアル(RxD)");
	sensors_pin_set("RXD0", "USBシリアル(TxD)");
	sensors_pin_set("EN", "リセットボタン");
	sensors_pin_set("IO" + String(PIN_SW),"操作ボタン");
	sensors_pin_set("IO" + String(PIN_LED),"状態表示LED");
	pinMode(PIN_LED,OUTPUT);					// LEDを接続したポートを出力に
	
	for(int i=0;i<sensors_devices_n;i++) sensors_devices_inited[i]=false;
	
	if(LCD_EN)			sensors_init_LCD(LCD_EN);
	if(TEMP_EN)			sensors_init_TEMP(1);
	if(HALL_EN)			sensors_init_HALL(1);
	if(ADC_EN)			sensors_init_ADC(ADC_EN);
	if(BTN_EN)			sensors_init_BTN(BTN_EN);
	if(PIR_EN)			sensors_init_PIR(1);
	if(AD_LUM_EN)		sensors_init_AD_LUM(1);
	if(AD_TEMP_EN)		sensors_init_AD_TEMP(AD_TEMP_EN);
	if(I2C_HUM_EN)		sensors_init_I2C_HUM(I2C_HUM_EN);
	if(I2C_ENV_EN)		sensors_init_I2C_ENV(I2C_ENV_EN);
	if(I2C_ACCEM_EN)	sensors_init_I2C_ACCEM(1);
}

boolean sensors_init_LED(int pin){
	String led_s="状態表示LED";
	if( pin == PIN_LED ) return true;
	sensors_pin_reset("IO" + String(PIN_LED),led_s);
	boolean ret = sensors_pin_set("IO" + String(pin),led_s);
	if(ret){
		pinMode(pin,OUTPUT);					// LEDを接続したポートを出力に
		digitalWrite(pin,HIGH);
		PIN_LED = pin;
	}else sensors_pin_reset("IO" + String(pin),led_s);
	return ret;
}

boolean sensors_init_LCD(int mode){
	boolean ret = true;		// ピン干渉なし
	if( mode == 0 ) LCD_EN=0;
	if( mode >= 1 && mode <=2){
		if( BOARD_TYPE == 2 ){	// TTGO
			if( sensors_pin_set("IO13","LCD_GND") &&
				sensors_pin_set("IO12","LCD_SDA") &&
				sensors_pin_set("IO14","LCD_SCL") &&
				sensors_pin_set("IO27","LCD_RESET") &&
				sensors_pin_set("IO26","LCD_VDD")
			){	pinMode(13,OUTPUT);	digitalWrite(13,LOW);
				pinMode(27,OUTPUT);	digitalWrite(27,LOW);
				pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
				for(int i=0;i<100;i++)delay(1);	// 待ち時間処理
				digitalWrite(27,HIGH);
				if( i2c_lcd_Setup(12, 14, mode * 8, 2) ) LCD_EN=mode;
			}else{
				ret = false;		// ピン干渉
				LCD_EN=0;
			}
		}else{
			/*	LCD	ESP
				VDD		IO19
				RESET	IO18
				SCL		IO5
				SDA		IO17
				GND		IO16
			*/
			if( sensors_pin_set("IO16","LCD_GND") &&
				sensors_pin_set("IO17","LCD_SDA") &&
				sensors_pin_set("IO5","LCD_SCL") &&
				sensors_pin_set("IO18","LCD_RESET") &&
				sensors_pin_set("IO19","LCD_VDD")
			){	pinMode(16,OUTPUT);	digitalWrite(16,LOW);
				pinMode(18,OUTPUT);	digitalWrite(18,LOW);
				pinMode(19,OUTPUT);	digitalWrite(19,HIGH);
				for(int i=0;i<100;i++)delay(1);	// 待ち時間処理
				digitalWrite(18,HIGH);
				if( i2c_lcd_Setup(17, 5, mode * 8, 2) ) LCD_EN=mode;
			}else{
				ret = false;		// ピン干渉
				LCD_EN=0;
			}
		}
	}
	if( BOARD_TYPE == 2 ){	// TTGO
		if(LCD_EN != 1 && LCD_EN !=2 ){
			sensors_pin_reset("IO13","LCD_GND");
			sensors_pin_reset("IO12","LCD_SDA");
			sensors_pin_reset("IO14","LCD_SCL");
			sensors_pin_reset("IO27","LCD_RESET");
			sensors_pin_reset("IO26","LCD_VDD");
		}
	}else{
		if(LCD_EN != 1 && LCD_EN !=2 ){
			sensors_pin_reset("IO16","LCD_GND");
			sensors_pin_reset("IO17","LCD_SDA");
			sensors_pin_reset("IO5","LCD_SCL");
			sensors_pin_reset("IO18","LCD_RESET");
			sensors_pin_reset("IO19","LCD_VDD");
		}
	}
	return ret;
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
	boolean ret = false;		// ピン干渉なし
	int i;
	for(i=1;i<5;i++){
		if(pin == sensors_adc_pin[i]){
			if(sensors_pin_set("IO" + String(pin),"アナログ_IN")){
				ADC_EN=pin;
				mvAnalogIn_init(ADC_EN);
				ret = true;
			}else{
				sensors_pin_reset("IO" + String(sensors_adc_pin[i]),"アナログ_IN");
			}
		}else sensors_pin_reset("IO" + String(sensors_adc_pin[i]),"アナログ_IN");
	}
	if(ret == false) ADC_EN=0;
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
		if( IR_IN_EN ) return false;	// IR と排他 ∵VDD=26/GND=14
		PIN_VDD = 25;
		PIN_PIR = 26;
		PIN_GND = 27;
		if(	sensors_pin_set("IO" + String(PIN_GND),"人感_GND") &&
			sensors_pin_set("IO" + String(PIN_PIR),"人感_OUT") &&
			sensors_pin_set("IO" + String(PIN_VDD),"人感_VIN")
		){	pinMode(PIN_GND,OUTPUT);	digitalWrite(PIN_GND,LOW);
			pinMode(PIN_PIR,INPUT);
			pinMode(PIN_VDD,OUTPUT);	digitalWrite(PIN_VDD,HIGH);
			PIR_EN=true;
		}else{
			ret = false;		// ピン干渉
			PIR_EN=false;
		}
	}else PIR_EN=false;
	
	if(!PIR_EN){
		sensors_pin_reset("IO" + String(PIN_GND),"人感_GND");
		sensors_pin_reset("IO" + String(PIN_PIR),"人感_OUT");
		sensors_pin_reset("IO" + String(PIN_VDD),"人感_VIN");
	}
	return ret;
}

boolean sensors_init_IR_IN(int mode){
	boolean ret = true;		// ピン干渉なし
	if( mode > 0 ){
		if( PIR_EN ) return false;	// PIR と排他 ∵VDD=14/GND=27
		PIN_IR_IN = 26;
		PIN_GND = 27;
		PIN_VDD = 14;
		if(	sensors_pin_set("IO" + String(PIN_GND),"赤外線_GND") &&
			sensors_pin_set("IO" + String(PIN_IR_IN),"赤外線_OUT") &&
			sensors_pin_set("IO" + String(PIN_VDD),"赤外線_VCC")
		){	pinMode(PIN_GND,OUTPUT);	digitalWrite(PIN_GND,LOW);
			pinMode(PIN_IR_IN,INPUT);
			pinMode(PIN_VDD,OUTPUT);	digitalWrite(PIN_VDD,HIGH);
			IR_IN_EN=mode;
		}else{
			ret = false;		// ピン干渉
			IR_IN_EN=0;
		}
	}else IR_IN_EN=0;
	
	if(!IR_IN_EN){
		sensors_pin_reset("IO" + String(PIN_GND),"赤外線_GND");
		sensors_pin_reset("IO" + String(PIN_IR_IN),"赤外線_OUT");
		sensors_pin_reset("IO" + String(PIN_VDD),"赤外線_VCC");
	}
	return ret;
}



boolean sensors_init_AD_LUM(int enable){
	boolean ret = true;		// ピン干渉なし
	if( enable > 0 ){
		if(	sensors_pin_set("IO32","照度_GND") &&
			sensors_pin_set("IO" + String(PIN_LUM),"照度_VOUT") &&
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
		sensors_pin_reset("IO" + String(PIN_LUM),"照度_VOUT");
		sensors_pin_reset("IO25","照度_+V");
	}
	return ret;
}

boolean sensors_init_AD_TEMP(int mode){
	boolean ret = true;		// ピン干渉なし
	if( mode == 0) AD_TEMP_EN=0;
	if( mode >= 1 && mode <= 2 ){
		if(	sensors_pin_set("IO32","温度_GND") &&
			sensors_pin_set("IO" + String(PIN_TEMP),"温度_VOUT") &&
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
		sensors_pin_reset("IO" + String(PIN_TEMP),"温度_VOUT");
		sensors_pin_reset("IO25","温度_+V");
		AD_TEMP_EN=0;
	}
	return ret;
}

void _sensors_init_I2C_HUM_reset_pin(int mode){
	if(mode != 1){
		sensors_pin_reset("IO13","SHT31_GND");
		sensors_pin_reset("IO12","SHT31_ADR");
		sensors_pin_reset("IO14","SHT31_SCL");
		sensors_pin_reset("IO27","SHT31_SDA");
		sensors_pin_reset("IO26","SHT31_VDD");
	}
	if(mode != 2){
		sensors_pin_reset("IO27","Si7021_GND");
		sensors_pin_reset("IO14","Si7021_SCL");
		sensors_pin_reset("IO12","Si7021_SDA");
		sensors_pin_reset("IO26","Si7021_VIN");
	}
	if(mode != 3){
		sensors_pin_reset("IO14","AM2320_GND");
		sensors_pin_reset("IO12","AM2320_SCL");
		sensors_pin_reset("IO27","AM2320_SDA");
		sensors_pin_reset("IO26","AM2320_VIN");
	}
	if(mode != 4){
		sensors_pin_reset("IO12","AM2302_GND");
		sensors_pin_reset("IO14","AM2302_NC");
		sensors_pin_reset("IO27","AM2302_SDA");
		sensors_pin_reset("IO26","AM2302_VIN");
	}
	if(mode != 5){
		sensors_pin_reset("IO12","DHT11_GND");
		sensors_pin_reset("IO14","DHT11_NC");
		sensors_pin_reset("IO27","DHT11_SDA");
		sensors_pin_reset("IO26","DHT11_VIN");
	}
}

boolean sensors_init_I2C_HUM(int mode){
	boolean ret = true;		// ピン干渉なし
	if( mode != I2C_HUM_EN ) _sensors_init_I2C_HUM_reset_pin(mode);
	if( mode == 0) I2C_HUM_EN=0;
	if( mode == 1){
		/*	SHT31	ESP
			VDD		IO26
			SDA		IO27
			SCL		IO14
			ADR		IO12	High 0x45
			GND		IO13 or GND
		*/
		if( sensors_pin_set("IO13","SHT31_GND") &&
			sensors_pin_set("IO12","SHT31_ADR") &&
			sensors_pin_set("IO14","SHT31_SCL") &&
			sensors_pin_set("IO27","SHT31_SDA") &&
			sensors_pin_set("IO26","SHT31_VDD")
		){	pinMode(13,OUTPUT);	digitalWrite(13,LOW);
			pinMode(12,OUTPUT);	digitalWrite(12,HIGH);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			if( i2c_sht31_Setup(27,14) ) sensors_WireBegin=true;
			I2C_HUM_EN=1;
		}else{
			ret = false;		// ピン干渉
			I2C_HUM_EN=0;
		}
	}
	if( mode == 2){
		/*	Si7021	ESP
			VIN		IO26
			GND		IO27
			SCL		IO14
			SDA		IO12
		*/
		if( sensors_pin_set("IO27","Si7021_GND") &&
			sensors_pin_set("IO14","Si7021_SCL") &&
			sensors_pin_set("IO12","Si7021_SDA") &&
			sensors_pin_set("IO26","Si7021_VIN")
		){	pinMode(27,OUTPUT);	digitalWrite(27,LOW);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			if( i2c_si7021_Setup(12,14) ) sensors_WireBegin=true;
			I2C_HUM_EN=2;
		}else{
			ret = false;		// ピン干渉
			I2C_HUM_EN=0;
		}
	}
	if( mode == 3){
		/*	AM2320	ESP
			VIN		IO26
			SDA		IO27
			GND		IO14
			SCL		IO12
		*/
		if( sensors_pin_set("IO14","AM2320_GND") &&
			sensors_pin_set("IO12","AM2320_SCL") &&
			sensors_pin_set("IO27","AM2320_SDA") &&
			sensors_pin_set("IO26","AM2320_VIN")
		){	pinMode(14,OUTPUT);	digitalWrite(14,LOW);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			if( i2c_am2320_Setup(27,12) ) sensors_WireBegin=true;
			I2C_HUM_EN=3;
		}else{
			ret = false;		// ピン干渉
			I2C_HUM_EN=0;
		}
	}
	if( mode == 4 ){
		/*	AM2302	ESP
			VIN		IO26
			SDA		IO27
			NC		IO14
			GND		IO12
		*/
		if( sensors_pin_set("IO12","AM2302_GND") &&
			sensors_pin_set("IO14","AM2302_NC") &&
			sensors_pin_set("IO27","AM2302_SDA") &&
			sensors_pin_set("IO26","AM2302_VIN")
		){	pinMode(12,OUTPUT);	digitalWrite(12,LOW);
			pinMode(14,INPUT_PULLDOWN);
			pinMode(27,INPUT_PULLUP);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			if( i2c_dht_Setup( 22 )) I2C_HUM_EN = 4;
		}else{
			ret = false;		// ピン干渉
			I2C_HUM_EN=0;
		}
	}
	if( mode == 5 ){
		if( sensors_pin_set("IO12","DHT11_GND") &&
			sensors_pin_set("IO14","DHT11_NC") &&
			sensors_pin_set("IO27","DHT11_SDA") &&
			sensors_pin_set("IO26","DHT11_VIN")
		){	pinMode(12,OUTPUT);	digitalWrite(12,LOW);
			pinMode(14,INPUT_PULLDOWN);
			pinMode(27,INPUT_PULLUP);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			if( i2c_dht_Setup( 11 )) I2C_HUM_EN = 5;
		}else{
			ret = false;		// ピン干渉
			I2C_HUM_EN=0;
		}
	}
	_sensors_init_I2C_HUM_reset_pin(I2C_HUM_EN);
	return ret;
}

boolean sensors_init_I2C_ENV(int mode){
	boolean ret = true;		// ピン干渉なし
	if( mode == 0 ) I2C_ENV_EN = 0;
	if( mode >= 1 && mode <=2){
		/*	BME280	ESP
			VCC		IO25
			GND		IO26
			SCL		IO27
			SDA		IO14
			CSB		IO12	High
			SD0		IO13 or GND	ADR=0x76
		*/
		if( sensors_pin_set("IO26","BME280_GND") &&
			sensors_pin_set("IO13","BME280_SD0") &&
			sensors_pin_set("IO27","BME280_SCL") &&
			sensors_pin_set("IO14","BME280_SDA") &&
			sensors_pin_set("IO12","BME280_CSB") &&
			sensors_pin_set("IO25","BME280_VDD")
		){	pinMode(26,OUTPUT);	digitalWrite(26,LOW);
			pinMode(13,OUTPUT);	digitalWrite(13,LOW);
			pinMode(12,OUTPUT);	digitalWrite(12,HIGH);
			pinMode(25,OUTPUT);	digitalWrite(25,HIGH);
			if( i2c_bme280_Setup(14,27) ) sensors_WireBegin=true;
			I2C_ENV_EN=mode;
		}else{
			ret = false;		// ピン干渉
			I2C_ENV_EN=0;
		}
	}
	if(I2C_ENV_EN != 1 && I2C_ENV_EN !=2 ){
		sensors_pin_reset("IO26","BME280_GND");
		sensors_pin_reset("IO13","BME280_SD0");
		sensors_pin_reset("IO27","BME280_SCL");
		sensors_pin_reset("IO14","BME280_SDA");
		sensors_pin_reset("IO12","BME280_CSB");
		sensors_pin_reset("IO25","BME280_VDD");
	}
	return ret;
}
boolean sensors_init_I2C_ACCEM(int enable){
	boolean ret = true;		// ピン干渉なし
	if( enable == 0 ) I2C_ACCEM_EN = false;
	if( enable > 0 ){
		/*	TTGO
			ADXL345	ESP
			GND		IO32
			VCC		IO33
			CS		IO34	OPEN PUP/High I2C
			INT1	IO35	IN
			INT2	IO25	IN
			SD0		IO26	High 0x1D
			SDA		IO27
			SCL		IO14
			
			DevC
			ADXL345	ESP
			SCL		IO32
			SDA		IO33
			SD0		IO25	High 0x1D
			INT2	IO26
			INT1	IO27
			CS		IO14	High I2C
			VCC		IO12
			GND		IO13
		*/
		if( BOARD_TYPE == 2 ){	// TTGO
			if( sensors_pin_set("IO32","ADXL321_GND") &&
				sensors_pin_set("IO34","ADXL321_CS") &&
				sensors_pin_set("IO35","ADXL321_INT1") &&
				sensors_pin_set("IO25","ADXL321_INT2") &&
				sensors_pin_set("IO27","ADXL321_SDA") &&
				sensors_pin_set("IO14","ADXL321_SCL") &&
				sensors_pin_set("IO26","ADXL321_SD0") &&
				sensors_pin_set("IO33","ADXL321_VCC")
			){	pinMode(32,OUTPUT);	digitalWrite(32,LOW);
				pinMode(34,INPUT_PULLUP);
				pinMode(35,INPUT_PULLUP);
				pinMode(25,INPUT_PULLUP);
				pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
				pinMode(33,OUTPUT);	digitalWrite(33,HIGH);
				if( i2c_adxl_Setup(27,14,0) ) sensors_WireBegin=true;
				I2C_ACCEM_EN=true;
			}else{
				ret = false;		// ピン干渉
				I2C_ACCEM_EN=false;
			}
		}else{
			if( sensors_pin_set("IO13","ADXL321_GND") &&
				sensors_pin_set("IO14","ADXL321_CS") &&
				sensors_pin_set("IO27","ADXL321_INT1") &&
				sensors_pin_set("IO26","ADXL321_INT2") &&
				sensors_pin_set("IO33","ADXL321_SDA") &&
				sensors_pin_set("IO32","ADXL321_SCL") &&
				sensors_pin_set("IO25","ADXL321_SD0") &&
				sensors_pin_set("IO12","ADXL321_VCC")
			){	pinMode(13,OUTPUT);	digitalWrite(13,LOW);
				pinMode(14,INPUT_PULLUP);
				pinMode(27,INPUT_PULLUP);
				pinMode(26,INPUT_PULLUP);
				pinMode(25,OUTPUT);	digitalWrite(25,HIGH);
				pinMode(12,OUTPUT);	digitalWrite(12,HIGH);
				if( i2c_adxl_Setup(33,32,0) ) sensors_WireBegin=true;
				I2C_ACCEM_EN=true;
			}else{
				ret = false;		// ピン干渉
				I2C_ACCEM_EN=false;
			}
		}
	}
	if(I2C_ACCEM_EN == false){
		sensors_pin_reset("IO32","ADXL321_GND");
		sensors_pin_reset("IO34","ADXL321_CS");
		sensors_pin_reset("IO35","ADXL321_INT1");
		sensors_pin_reset("IO25","ADXL321_INT2");
		sensors_pin_reset("IO27","ADXL321_SDA");
		sensors_pin_reset("IO14","ADXL321_SCL");
		sensors_pin_reset("IO26","ADXL321_SD0");
		sensors_pin_reset("IO33","ADXL321_VCC");
		
		sensors_pin_reset("IO13","ADXL321_GND");
		sensors_pin_reset("IO14","ADXL321_CS");
		sensors_pin_reset("IO27","ADXL321_INT1");
		sensors_pin_reset("IO26","ADXL321_INT2");
		sensors_pin_reset("IO33","ADXL321_SDA");
		sensors_pin_reset("IO32","ADXL321_SCL");
		sensors_pin_reset("IO25","ADXL321_SD0");
		sensors_pin_reset("IO12","ADXL321_VCC");
	}
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
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(temp);
		sensors_S += "温度(℃)";
		if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[0], String(temp));
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
		if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[1], String(hall));
	}
	if(ADC_EN){
		int adc = (int)mvAnalogIn(ADC_EN);
		Serial.print("adc        = ");
		Serial.println(adc);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(adc);
		sensors_S += "ADC(mV)";
		if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[2], String(adc));
	}
	if(BTN_EN>0){
		pinMode(PIN_SW,INPUT_PULLUP);
		int btn = !digitalRead(PIN_SW);		// open=0,HIGH, push=1,LOW
		if( sensors_btnPush_b ) btn =1;
		boolean btn_b = (boolean)btn;
		Serial.print("btn        = ");
		Serial.println(btn);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(btn);
		sensors_S += "ボタン";
		if(sensors_btnPrev_b != btn_b || sensors_btnPush_b){
			if(BTN_EN==2){
				if( btn_b ) sensors_sendUdp("Ping");
				else        sensors_sendUdp("Pong");
			}else{
				if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[3], String(btn));
			}
		}
		sensors_btnPush_b = false;
		sensors_btnPrev_b = btn_b;
	}
	if(PIR_EN){
		int pir = digitalRead(PIN_PIR);
		if( sensors_pirPush_b ) pir =1;
		boolean pir_b = (boolean)pir;
		Serial.print("pir        = ");
		Serial.println(pir);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(pir);
		sensors_S += "人感";
		if(sensors_pirPrev_b != pir_b || sensors_pirPush_b){
			if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[4], String(pir));
		}
		sensors_pirPush_b = false;
		sensors_pirPrev_b = pir_b;
	}
	if(IR_IN_EN){
		Serial.print("ir_in      = ");
		Serial.println(sensor_ir_data8);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload += String(sensor_ir_data8);
		sensors_S += "赤外RC";
	}
	if(AD_LUM_EN){
		float lum = (float)analogRead(PIN_LUM) / 4096. * 3100 ;  // 直読み値
		lum *= 100. / 33.;                      // 照度(lx)へ変換
		int lum_i = (int)lum;
		Serial.print("illum      = ");
		Serial.println(lum_i);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(lum_i);
		sensors_S += "照度(lx)";
		if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[5], String(lum_i));
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
		Serial.println("temp.      = " + temp_S);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(temp_S);
		sensors_S += "温度(℃)";
		if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[6], temp_S);
	}
	if(I2C_HUM_EN>0){		// 1:SHT31, 2:Si7021, 3:AM2320, 4:AM2302, 5:DHT11
		float temp = -999, hum = -999;
		if( I2C_HUM_EN == 1){
			if( !sensors_WireBegin && i2c_sht31_Setup(27,14) ) sensors_WireBegin=true;
			temp = i2c_sht31_getTemp();
			hum = i2c_sht31_getHum();
		}
		if( I2C_HUM_EN == 2){
			if( !sensors_WireBegin && i2c_si7021_Setup(12,14) ) sensors_WireBegin=true;
			temp = i2c_si7021_getTemp();
			hum = i2c_si7021_getHum();
		}
		if( I2C_HUM_EN == 3){
			if( !sensors_WireBegin && i2c_am2320_Setup(27,12) ) sensors_WireBegin=true;
			temp = i2c_am2320_getTemp();
			hum = i2c_am2320_getHum();
		}
		if( I2C_HUM_EN == 4 || I2C_HUM_EN == 5){
			temp = i2c_dht_getTemp();
			hum = i2c_dht_getHum();
		}
		String hum_S = dtoStrf(temp,1) + ", " + dtoStrf(hum,0);
		Serial.print("humid      = ");
		Serial.println(hum_S);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(hum_S);
		sensors_S += "温度(℃), 湿度(％)";
		if(temp >= -100 && hum >= 0 ){
			if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[7], hum_S);
		}else{
			Serial.println("ERROR: i2c");
			sensors_S += "ERR";
			hum_S = "0, 0";
		}
	}
	if(I2C_ENV_EN>0){		// 1:BME280, 2:BMP280
		float temp = -999, hum = -999, press = -999;
		if( !sensors_WireBegin && i2c_bme280_Setup(14,27) ) sensors_WireBegin=true;
		temp = i2c_bme280_getTemp();
		press = i2c_bme280_getPress();
		
		String env_S = dtoStrf(temp,1);
		if( I2C_ENV_EN == 1){
			hum = i2c_bme280_getHum();
			env_S += ", " + dtoStrf(hum,0);
			Serial.print("envir      = ");
		}else{
			Serial.print("press      = ");
		}
		env_S += ", " + dtoStrf(press,0);
		Serial.println(env_S);
		
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(env_S);
		sensors_S += "温度(℃)";
		if( I2C_ENV_EN == 1){	// BME280 (湿度センサ付き)
			sensors_csv(sensors_S,csv_b);
			sensors_S += "湿度(％), 気圧(hPa)";
			if( temp < 100 && hum >= 0 && press < 2000 ){
				if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[9], env_S);
			}else{
				Serial.println("ERROR: i2c");
				sensors_S += "ERR";
				env_S = "0, 0, 0";
			}
		}else{					// BMP280 (湿度センサ無し)
			sensors_csv(sensors_S,csv_b);
			sensors_S += "気圧(hPa)";
			if( temp < 100 && press < 2000 ){
				if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[8], env_S);
			}else{
				Serial.println("ERROR: i2c");
				sensors_S += "ERR";
				env_S = "0, 0";
			}
		}
	}
	if(I2C_ACCEM_EN){
		if( !sensors_WireBegin ){
			if( BOARD_TYPE == 2 ){	// TTGO
				if( i2c_adxl_Setup(27,14,0) ) sensors_WireBegin=true;
			}else{
				if( i2c_adxl_Setup(33,32,0) ) sensors_WireBegin=true;
			}
		}
		
		float acm[3];
		String acm_S = "";
		for(int i=0;i<3;i++){
			acm[i] = i2c_adxl_getAcm(i);
			acm_S += dtoStrf(acm[i],1);
			if(i < 2 ) acm_S += ", ";
		}
		Serial.println("accem      = " + acm_S);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(acm_S);
		sensors_S += "加速度x(m/s2),y(m/s2),z(m/s2)";
		if(acm[0] > -99 && acm[1] > -99  && acm[2] > -99 ){
			if(UDP_MODE & 1) sensors_sendUdp(sensors_devices[10], acm_S);
		}else{
			Serial.println("ERROR: i2c");
			sensors_S += "ERR";
			acm_S = "0, 0, 0";
		}
	}
	if(TIMER_EN){
		String timer_S = dtoStrf((float)millis() / 1000,1);
		Serial.println("timer      = " + timer_S);
		sensors_csv(payload,csv_b);
		sensors_csv(sensors_S,csv_b);
		csv_b = true;
		payload +=  String(timer_S);
		sensors_S += "時間(秒)";
	}
	
	if(UDP_MODE & 2) sensors_sendUdp(DEVICE, payload);
	if(LCD_EN && payload.length() > 0){
		i2c_lcd_print_S( &payload );
	}
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
		for(int i=0;i<10;i++)delay(1);	// 待ち時間処理
		return S;
	}
	return "";
}
