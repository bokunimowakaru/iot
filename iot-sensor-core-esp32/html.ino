#include <WiFiClient.h>
#include <WebServer.h>
#define html_title "IoT Sensor Core ESP32"
#define HTML_INDEX_LEN_MAX	5000
#define HTML_MISC_LEN_MAX	1024
#define HTML_RES_LEN_MAX	128

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

WebServer server(80);							// Webサーバ(ポート80=HTTP)定義

uint32_t	html_ip=0;
char 		html_ip_s[16];
const char	html_checked[2][18]={"","checked=\"checked\""};
const byte	html_adc_vals[5]={0,32,33,34,35};

const String html_PINOUT_S[38] = {
	"GND","3V3","EN","SVP","SVN","IO34","IO35","IO32","IO33","IO25","IO26","IO27","IO14","IO12","GND","IO13","SD2","SD3","CMD",
	"CLK","SDD","SD1","IO15","IO2","IO0","IO4","IO16","IO17","IO5","IO18","IO19","NC","IO21","RXD0","TXD0","IO22","IO23","GND"};

String html_PIN_ASSIGNED_S[38] = {
	"電池(-)","電池(+)","リセットボタン","SVP","SVN","IO34","IO35","IO32","IO33","IO25","IO26","IO27","IO14","IO12","GND","IO13","","","",
	"","","","IO15","IO2","ボタン","IO4","IO16","IO17","IO5","IO18","IO19","","IO21","USBシリアル(TxD)","USBシリアル(RxD)","IO22","IO23","GND"};
	
	/* Null = ピンの無いもの、PINOUTと同値 = ピンアサインの無いもの */

boolean html_pin_set(String pin, String name){
	for(int i=0; i< 38;i++){
		if( pin.equals(html_PINOUT_S[i]) ){
			if( html_PIN_ASSIGNED_S[i].equals(html_PINOUT_S[i]) ){
				html_PIN_ASSIGNED_S[i] = name;
				return true;
			}
			if( html_PIN_ASSIGNED_S[i].equals(name) ){
				return true;
			}
			return false;
		}
	}
	return false;
}

boolean html_pin_reset(String pin, String name){
	for(int i=0; i< 38;i++){
		if( pin.equals(html_PINOUT_S[i]) ){
			if( html_PIN_ASSIGNED_S[i].equals(name) ){
				html_PIN_ASSIGNED_S[i] = html_PINOUT_S[i];
				return true;
			}
			return false;
		}
	}
	return false;
}

boolean html_check_overrun(int len){
	Serial.print("done html, ");
	Serial.print(len);
	Serial.println(" bytes");
	if(HTML_INDEX_LEN_MAX - 1 <= len){
		Serial.println("ERROR: Prevented Buffer Overrun");
		return false;
	}
	return true;
}

void html_index(){
	char s[HTML_INDEX_LEN_MAX];
	char res_s[HTML_RES_LEN_MAX]="待機中";
	char sensors_s[HTML_RES_LEN_MAX]="";
	int i;
	
	Serial.println("HTML index");
	
	if(server.hasArg("SLEEP_SEC")){
		int sleep_i = server.arg("SLEEP_SEC").toInt();
		if(sleep_i >=0 && sleep_i <= 65535 && sleep_i != SLEEP_SEC){
			SLEEP_SEC = sleep_i;
			if(SLEEP_SEC == 65535 )	snprintf(res_s, HTML_RES_LEN_MAX,"スリープを[ON]に設定しました。ボタンや人感センサを設定していないと起動しません。");
			else if(SLEEP_SEC == 0)	snprintf(res_s, HTML_RES_LEN_MAX,"スリープを[OFF]に設定しました。電力を多く消費するのでUSB等から給電してください。");
			else					snprintf(res_s, HTML_RES_LEN_MAX,"間欠動作間隔を[%d]分[%d]秒に設定しました。スリープ中は操作できません。",(sleep_i+5)/60,(sleep_i+5)%60);
			Serial.print(" SLEEP_SEC=");
			Serial.println(SLEEP_SEC);
		}
	}
	
	if(server.hasArg("TEMP_EN")){
		i = server.arg("TEMP_EN").toInt();
		if( i==0 ) TEMP_EN=false;
		if( i==1 ) TEMP_EN=true;
		Serial.print(" TEMP_EN=");
		Serial.println(TEMP_EN);
	}
	if(server.hasArg("TEMP_ADJ")){
		i = server.arg("TEMP_ADJ").toInt();
		if( i >= -100 && i <= 100 ){
			TEMP_ADJ = i;
			Serial.print(" TEMP_ADJ=");
			Serial.println(TEMP_ADJ);
		}
	}
	if(server.hasArg("HALL_EN")){
		i = server.arg("HALL_EN").toInt();
		if( i==0 ) HALL_EN=false;
		if( i==1 ) HALL_EN=true;
		Serial.print(" HALL_EN=");
		Serial.println(HALL_EN);
	}
	if(server.hasArg("ADC_EN")){
		int adc = server.arg("ADC_EN").toInt();
		for(i=1;i<5;i++){
			if(adc == html_adc_vals[i]){
				if(html_pin_set("IO" + String(adc),"アナログ_IN")){
					ADC_EN=adc;
					mvAnalogIn_init(ADC_EN);
				}
			}else{
				html_pin_reset("IO" + String(html_adc_vals[i]),"アナログ_IN");
			}
		}
		if(i==5) ADC_EN=0;
		Serial.print(" ADC_EN=");
		Serial.println(ADC_EN);
	}
	if(server.hasArg("BTN_EN")){
		i = server.arg("BTN_EN").toInt();
		if( i >= 0 && i <= 2) BTN_EN=i;
		Serial.print(" BTN_EN=");
		Serial.println(BTN_EN);
	}
	if(server.hasArg("PIR_EN")){
		i = server.arg("PIR_EN").toInt();
		if( i==1 &&
			html_pin_set("IO14","人感_GND") &&
			html_pin_set("IO" + String(PIN_PIR),"人感_IN") &&
			html_pin_set("IO26","人感_VDD")
		){	pinMode(14,OUTPUT);	digitalWrite(14,LOW);
			pinMode(PIN_PIR,INPUT);
			pinMode(26,OUTPUT);	digitalWrite(26,HIGH);
			PIR_EN=true;
		}else{
			html_pin_reset("IO14","人感_GND");
			html_pin_reset("IO" + String(PIN_PIR),"人感_IN");
			html_pin_reset("IO26","人感_VIN");
			if(i) snprintf(res_s, HTML_RES_LEN_MAX,"人感センサの設定に失敗しました。");
			PIR_EN=false;
		}
		Serial.print(" PIR_EN=");
		Serial.println(PIR_EN);
	}
	if(server.hasArg("AD_LUM_EN")){
		i = server.arg("AD_LUM_EN").toInt();
		if( i==1 &&
			html_pin_set("IO32","照度_GND") &&
			html_pin_set("IO" + String(PIN_LUM),"照度_IN") &&
			html_pin_set("IO25","照度_VDD")
		){	pinMode(32,OUTPUT);	digitalWrite(32,LOW);
			pinMode(PIN_PIR,INPUT_PULLDOWN);
			pinMode(25,OUTPUT);	digitalWrite(25,HIGH);
			AD_LUM_EN=true;
		}else{
			html_pin_reset("IO32","照度_GND");
			html_pin_reset("IO" + String(PIN_LUM),"照度_IN");
			html_pin_set("IO25","照度_VDD");
			if(i) snprintf(res_s, HTML_RES_LEN_MAX,"照度センサの設定に失敗しました。");
			AD_LUM_EN=false;
		}
		Serial.print(" AD_LUM_EN=");
		Serial.println(AD_LUM_EN);
	}
	if(server.hasArg("AD_TEMP_EN")){
		i = server.arg("AD_TEMP_EN").toInt();
		if( i >= 1 && i <= 2 &&
			html_pin_set("IO32","温度_GND") &&
			html_pin_set("IO" + String(PIN_TEMP),"温度_IN") &&
			html_pin_set("IO25","温度_VDD")
		){	pinMode(32,OUTPUT);	digitalWrite(32,LOW);
			pinMode(PIN_TEMP,INPUT);
			pinMode(25,OUTPUT);	digitalWrite(25,HIGH);
			AD_TEMP_EN=i;
		}else{
			html_pin_reset("IO32","温度_GND");
			html_pin_reset("IO" + String(PIN_TEMP),"温度_IN");
			html_pin_reset("IO25","温度_VDD");
			if(i) snprintf(res_s, HTML_RES_LEN_MAX,"温度センサの設定に失敗しました。");
			AD_TEMP_EN=0;
		}
		Serial.print(" AD_TEMP_EN=");
		Serial.println(AD_TEMP_EN);
	}
	if(server.hasArg("I2C_HUM_EN")){
		i = server.arg("I2C_HUM_EN").toInt();
		if( i >= 1 && i <=2 ){
			if( i == 1){
				if( html_pin_set("IO13","SHT31_ADR") &&
					html_pin_set("IO12","SHT31_I2C_SCL") &&
					html_pin_set("IO14","SHT31_I2C_SDA") &&
					html_pin_set("IO27","SHT31_VDD")
				){	pinMode(13,OUTPUT);	digitalWrite(13,HIGH);
					pinMode(27,OUTPUT);	digitalWrite(27,HIGH);
					i2c_sht31_Setup(14,12);
					I2C_HUM_EN=1;
				}else{
					html_pin_reset("IO13","SHT31_ADR");
					html_pin_reset("IO12","SHT31_I2C_SCL");
					html_pin_reset("IO14","SHT31_I2C_SDA");
					html_pin_reset("IO27","SHT31_VDD");
					if(i) snprintf(res_s, HTML_RES_LEN_MAX,"I2C温湿度センサの設定に失敗しました。");
					I2C_HUM_EN=0;
				}
			}
			if( i == 2){
			}
		}
		Serial.print(" I2C_HUM_EN=");
		Serial.println(I2C_HUM_EN);
	}
	if(server.hasArg("I2C_ENV_EN")){
		i = server.arg("I2C_ENV_EN").toInt();
		if( i >= 0 && i <= 2) I2C_ENV_EN=i;
		Serial.print(" I2C_ENV_EN=");
		Serial.println(I2C_ENV_EN);
	}
	if(server.hasArg("I2C_ACCUM_EN")){
		i = server.arg("I2C_ACCUM_EN").toInt();
		if( i==0 ) I2C_ACCUM_EN=false;
		if( i==1 ) I2C_ACCUM_EN=true;
		Serial.print(" I2C_ACCUM_EN=");
		Serial.println(I2C_ACCUM_EN);
	}
	
	if(server.hasArg("SENSORS")){
		strcpy(res_s,"センサ取得値=");
		int len=strlen(res_s);
		String payload = String(sensors_get());
		payload.toCharArray(&res_s[len],HTML_RES_LEN_MAX-len);
		if(UDP_PORT>0) sendUdp(payload);
	}
	sensors_name().toCharArray(sensors_s,HTML_RES_LEN_MAX);
	
	if(server.hasArg("DEVICE_NUM")){
		i = server.arg("DEVICE_NUM").toInt();
		if( i >= 0 && i <= 9 ){
			char c = (char)((int)'0'+i);
			if( DEVICE_NUM != c ){
				snprintf(res_s, HTML_RES_LEN_MAX,"デバイス番号を[%c]に設定しました",c);
				DEVICE_NUM = c;
				Serial.print(" DEVICE_NUM=");
				Serial.println(DEVICE_NUM);
			}
		}
	}
	
	if(server.hasArg("UDP_PORT")){
		i = server.arg("UDP_PORT").toInt();
		if( i >= 0 && i <= 65535 && UDP_PORT != i){
			UDP_PORT = i;
			if(i) snprintf(res_s, HTML_RES_LEN_MAX,"UDP送信ポート番号を[%d]に設定しました",i);
			else snprintf(res_s, HTML_RES_LEN_MAX,"UDP送信を[OFF]に設定しました");
			Serial.print(" UDP_PORT=");
			Serial.println(UDP_PORT);
		}
	}
	
	if(server.hasArg("AmbientChannelId")){
		int i = server.arg("AmbientChannelId").toInt();
		if( i != AmbientChannelId){
			AmbientChannelId = i;
			if(i) snprintf(res_s, HTML_RES_LEN_MAX,"Ambient ID を[%d]に設定しました",i);
			else snprintf(res_s, HTML_RES_LEN_MAX,"Ambientへの送信を[OFF]にしました");
			Serial.print(" AmbientChannelId=");
			Serial.println(AmbientChannelId);
		}
	}
	
	if(server.hasArg("AmbientWriteKey")){
		String S = server.arg("AmbientWriteKey");
		if( S.length() == 16 && S.equals(String(AmbientWriteKey)) == false ){
			S.toCharArray(AmbientWriteKey,17);
			snprintf(res_s, HTML_RES_LEN_MAX,"Ambient(ID=%d)のWriteKeyを[%s]に設定しました",AmbientChannelId,AmbientWriteKey);
		}
		Serial.print(" AmbientWriteKey=");
		Serial.println(AmbientWriteKey);
	}
	
	if(server.hasArg("SEND_INT_SEC")){
		i = server.arg("SEND_INT_SEC").toInt();
		if( SEND_INT_SEC != i){
			SEND_INT_SEC = i;
			if(i) snprintf(res_s, HTML_RES_LEN_MAX,"自動送信間隔(動作時)を[%d]に設定しました",i);
			else  snprintf(res_s, HTML_RES_LEN_MAX,"自動送信を[OFF]に設定しました");
			Serial.print(" SEND_INT_SEC=");
			Serial.println(SEND_INT_SEC);
		}
	}

	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
			</head>\
			<body>\
				<h1>%s</h1>\
				<hr>\
				<h3>状態</h3>\
					<p>%s</p>\
				<h3>有効なセンサ</h3>\
					<p>%s</p>\
				<h3>センサ値を取得</h3>\
					<p><a href=\"http://%s/?SENSORS=GET\">http://%s/?SENSORS=GET</a>\
					<form method=\"GET\" action=\"/\">\
					<input type=\"submit\" name=\"SENSORS\" value=\"取得\" size=\"4\">\
					</form></p>\
				<hr>\
				<h3>設定</h3>\
				<h4><a href=\"wifi\">Wi-Fi 設定</a></h4>\
				<h4><a href=\"sensors\">センサ設定</a></h4>\
				<h4><a href=\"sendto\">データ送信設定</a></h4>\
				<h4><a href=\"pinout\">ピン配列表</a></h4>\
				<hr>\
				<h3>電源</h3>\
				<h4><a href=\"reboot\">再起動</a></h4>\
				<h4><a href=\"sleep\">OFF（スリープ）</a></h4>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title, html_title, res_s, sensors_s, html_ip_s, html_ip_s
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_wifi(){
	char s[HTML_INDEX_LEN_MAX];
	char res_s[HTML_RES_LEN_MAX]="";
	int i;
	
	Serial.println("HTML Wi-Fi");
	
	if(server.hasArg("SSID")){
		String S = server.arg("SSID");
		int len = S.length();
		if( len > 15 ){
			strcpy(res_s,"エラー：接続先SSIDの文字数は15文字までです。");
		}else{
			if(server.hasArg("PASS")){
				String P = server.arg("PASS");
				len = P.length();
				if( len > 31 ){
					strcpy(res_s,"エラー：接続先PASSの文字数は31文字までです。");
				}else{
					S.toCharArray(SSID_STA,16);
					P.toCharArray(PASS_STA,32);
					snprintf(res_s, HTML_RES_LEN_MAX,"接続先SSIDを[%s]に設定しました(Wi-Fi再起動後に有効)。",SSID_STA);
					Serial.print(" SSID_STA=");
					Serial.print(SSID_STA);
					Serial.print(" PASS_STA=");
					Serial.println(PASS_STA);
					if(WIFI_AP_MODE & 2 != 2){
						WIFI_AP_MODE &= 2;
						snprintf(res_s, HTML_RES_LEN_MAX,"Wi-Fiモード(STA)とSSIDを設定しました(Wi-Fi再起動後に有効)。");
						Serial.print(" WIFI_AP_MODE=");
						Serial.println(WIFI_AP_MODE);
					}
				}
			}
		}
	}

	if(server.hasArg("SSID_AP")){
		String S = server.arg("SSID_AP");
		int len = S.length();
		if( len > 15 ){
			strcpy(res_s,"エラー：本機のSSIDの文字数は15文字までです。");
		}else{
			if(server.hasArg("PASS_AP")){
				String P = server.arg("PASS_AP");
				len = P.length();
				if( len > 15 ){
					strcpy(res_s,"エラー：本機のPASSの文字数は15文字までです。");
				}else{
					S.toCharArray(SSID_AP,16);
					P.toCharArray(PASS_AP,16);
					snprintf(res_s, HTML_RES_LEN_MAX,"本機のSSIDを[%s]に設定しました(Wi-Fi再起動後に有効)。",SSID_STA);
					Serial.print(" SSID_AP=");
					Serial.print(SSID_STA);
					Serial.print(" PASS_AP=");
					Serial.println(PASS_STA);
				}
			}
		}
	}
	
	if(server.hasArg("MODE")){
		String S = server.arg("MODE");
		i = S.toInt();
		if( i >= 1 && i <= 3 ){
			char mode_s[3][7]={"AP","STA","AP+STA"};
			WIFI_AP_MODE = i;
			snprintf(res_s, HTML_RES_LEN_MAX,"Wi-Fiモードを[%s]に設定しました(Wi-Fi再起動後に有効)。",mode_s[i-1]);
			Serial.print(" WIFI_AP_MODE=");
			Serial.println(WIFI_AP_MODE);
		}else strcpy(res_s,"エラー：Wi-Fiモードが範囲外です。");
	}
	
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s Wi-Fi 設定</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
			</head>\
			<body>\
				<h1>%s Wi-Fi 設定</h1>\
				<p>%s</p>\
				<hr>\
				<h3>Wi-Fi 動作モード</h3>\
				<form method=\"GET\" action=\"/wifi\">\
					<input type=\"radio\" name=\"MODE\" value=\"1\" %s>AP\
					<input type=\"radio\" name=\"MODE\" value=\"2\" %s>STA\
					<input type=\"radio\" name=\"MODE\" value=\"3\" %s>AP+STA\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
					<p>Wi-Fiモードを[STA]にすると無線LANが切断されます(操作不可になる)</p>\
					<p>[AP]:本機がAPとして動作, [STA]:他のAPへ接続, [AP+STA]:両方</p>\
				</form>\
				<hr>\
				<h3>Wi-Fi AP 設定</h3>\
				<form method=\"GET\" action=\"/wifi\">\
					<p>本機へ Wi-Fi AP(アクセスポイント)へ接続するための設定です。</p>\
					SSID=<input type=\"text\" name=\"SSID_AP\" value=\"%s\" size=\"15\">\
					PASS=<input type=\"password\" name=\"PASS_AP\" value=\"%s\" size=\"15\">\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
					<p>変更すると、Wi-Fi を新しい設定で再接続する必要があります。</p>\
				</form>\
				<hr>\
				<h3>Wi-Fi STA 接続先</h3>\
				<form method=\"GET\" action=\"/wifi\">\
					<p>お手持ちのWi-Fiアクセスポイントの設定を記入し[設定]を押してください。</p>\
					SSID=<input type=\"text\" name=\"SSID\" value=\"%s\" size=\"15\">\
					PASS=<input type=\"password\" name=\"PASS\" size=\"15\">\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
				</form>\
				<hr>\
				<h3>Wi-Fi 再起動</h3>\
				<form method=\"GET\" action=\"/reboot\">\
					<p>Wi-Fi 設定を有効にするために再起動を行ってください。</p>\
					<input type=\"submit\" name=\"BOOT\" value=\"再起動\" size=\"6\">\
				</form>\
				<hr>\
				<h3>スリープ設定</h3>\
				<form method=\"GET\" action=\"/\">\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"25\" %s>30秒\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"55\" %s>1分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"175\" %s>3分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"595\" %s>10分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"1795\" %s>30分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"3595\" %s>60分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"65535\" %s>∞\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
					<p>[OFF]以外に設定するとスリープ中(殆どの時間)は操作できません。</p>\
				</form>\
				<hr>\
				<form method=\"GET\" action=\"/\">\
					<input type=\"submit\" value=\"前の画面に戻る\">\
				</form>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title,
			html_title,  res_s,
			html_checked[WIFI_AP_MODE==1], html_checked[WIFI_AP_MODE==2], html_checked[WIFI_AP_MODE==3],
			SSID_AP, PASS_AP,
			SSID_STA,
			html_checked[SLEEP_SEC==0], html_checked[SLEEP_SEC==25], html_checked[SLEEP_SEC==55], html_checked[SLEEP_SEC==175],
			html_checked[SLEEP_SEC==595], html_checked[SLEEP_SEC==1795], html_checked[SLEEP_SEC==3595], html_checked[SLEEP_SEC==65535]
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_sensors(){
	char s[HTML_INDEX_LEN_MAX];
	int i;
	
	Serial.println("HTML sensors");
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s センサ設定</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
			</head>\
			<body>\
				<h1>%s センサ設定</h1>\
				<form method=\"GET\" action=\"/\">\
					<p>内蔵温度センサ　\
					<input type=\"radio\" name=\"TEMP_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"TEMP_EN\" value=\"1\" %s>ON\
					補正値=<input type=\"text\" name=\"TEMP_ADJ\" value=\"%d\" size=\"5\">℃\
					</p>\
					<p>内蔵磁気センサ　\
					<input type=\"radio\" name=\"HALL_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"HALL_EN\" value=\"1\" %s>ON\
					</p>\
					<p>ADCセンサ　\
					<input type=\"radio\" name=\"ADC_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"ADC_EN\" value=\"32\" %s>IO32\
					<input type=\"radio\" name=\"ADC_EN\" value=\"33\" %s>IO33\
					<input type=\"radio\" name=\"ADC_EN\" value=\"34\" %s>IO34\
					<input type=\"radio\" name=\"ADC_EN\" value=\"35\" %s>IO35\
					</p>\
					<p>押しボタン　\
					<input type=\"radio\" name=\"BTN_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"BTN_EN\" value=\"1\" %s>ON\
					<input type=\"radio\" name=\"BTN_EN\" value=\"2\" %s>PingPong\
					</p>\
					<p>人感センサ　\
					<input type=\"radio\" name=\"PIR_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"PIR_EN\" value=\"1\" %s>ON\
					</p>\
					<p>照度センサ　\
					<input type=\"radio\" name=\"AD_LUM_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"AD_LUM_EN\" value=\"1\" %s>NJL7502L\
					</p>\
					<p>温度センサ　\
					<input type=\"radio\" name=\"AD_TEMP_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"AD_TEMP_EN\" value=\"1\" %s>LM61\
					<input type=\"radio\" name=\"AD_TEMP_EN\" value=\"2\" %s>MCP9700\
					</p>\
					<p>温湿度センサ　\
					<input type=\"radio\" name=\"I2C_HUM_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"I2C_HUM_EN\" value=\"1\" %s>SHT31\
					<input type=\"radio\" name=\"I2C_HUM_EN\" value=\"2\" %s>Si7021\
					</p>\
					<p>環境センサ　\
					<input type=\"radio\" name=\"I2C_ENV_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"I2C_ENV_EN\" value=\"1\" %s>BME280\
					<input type=\"radio\" name=\"I2C_ENV_EN\" value=\"2\" %s>BMP280\
					</p>\
					<p>加速度センサ　\
					<input type=\"radio\" name=\"I2C_ACCUM_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"I2C_ACCUM_EN\" value=\"1\" %s>ADXL345\
					</p>\
					<p>センサ設定の実行　\
					<input type=\"submit\" name=\"SENSORS\" value=\"設定\" size=\"4\">\
					</p>\
				</form>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title,
			html_title,
				html_checked[!TEMP_EN], html_checked[TEMP_EN], TEMP_ADJ, 
				html_checked[!HALL_EN], html_checked[HALL_EN], 
				html_checked[ADC_EN==0], html_checked[ADC_EN==32], html_checked[ADC_EN==33], html_checked[ADC_EN==34], html_checked[ADC_EN==35],
				html_checked[BTN_EN==0], html_checked[BTN_EN==1], html_checked[BTN_EN==2],
				html_checked[PIR_EN==0], html_checked[PIR_EN==1],
				html_checked[AD_LUM_EN==0], html_checked[AD_LUM_EN==1],
				html_checked[AD_TEMP_EN==0], html_checked[AD_TEMP_EN==1], html_checked[AD_TEMP_EN==2],
				html_checked[I2C_HUM_EN==0], html_checked[I2C_HUM_EN==1], html_checked[I2C_HUM_EN==2],
				html_checked[I2C_ENV_EN==0], html_checked[I2C_ENV_EN==1], html_checked[I2C_ENV_EN==2],
				html_checked[I2C_ACCUM_EN==0], html_checked[I2C_ACCUM_EN==1]
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_sendto(){
	char s[HTML_INDEX_LEN_MAX];
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s データ送信設定</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
			</head>\
			<body>\
				<h1>%s データ送信設定</h1>\
				<form method=\"GET\" action=\"/\">\
					<h3>UDP送信設定</h3>\
					<p>ポート番号　\
					<input type=\"radio\" name=\"UDP_PORT\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"UDP_PORT\" value=\"1024\" %s>1024\
					<input type=\"radio\" name=\"UDP_PORT\" value=\"3054\" %s>3054\
					<input type=\"radio\" name=\"UDP_PORT\" value=\"49152\" %s>49152\
					</p>\
					<p>デバイス番号　\
					<input type=\"radio\" name=\"DEVICE_NUM\" value=\"1\" %s>1\
					<input type=\"radio\" name=\"DEVICE_NUM\" value=\"2\" %s>2\
					<input type=\"radio\" name=\"DEVICE_NUM\" value=\"3\" %s>3\
					<input type=\"radio\" name=\"DEVICE_NUM\" value=\"4\" %s>4\
					<input type=\"radio\" name=\"DEVICE_NUM\" value=\"5\" %s>5\
					</p>\
					<h3>Ambient 送信設定</h3>\
					ID=<input type=\"text\" name=\"AmbientChannelId\" value=\"%d\" size=\"5\"> (0:OFF)\
					WriteKey=<input type=\"text\" name=\"AmbientWriteKey\" value=\"%s\" size=\"18\">\
					<p><a href=\"http://ambidata.io/\">http://ambidata.io/</a></p>\
					<h3>自動送信間隔(常時動作時※)</h3>\
					<input type=\"radio\" name=\"SEND_INT_SEC\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"SEND_INT_SEC\" value=\"5\" %s>5秒\
					<input type=\"radio\" name=\"SEND_INT_SEC\" value=\"15\" %s>15秒\
					<input type=\"radio\" name=\"SEND_INT_SEC\" value=\"30\" %s>30秒\
					<input type=\"radio\" name=\"SEND_INT_SEC\" value=\"60\" %s>60秒\
					<p>※スリープ中は本設定に関わらず、[Wi-Fi 設定]の[スリープ間隔]で送信します。</p>\
					<p>Ambientへの送信間隔は30秒以上を推奨します(1日3000サンプルまで)。</p>\
					<h3>送信設定の実行</h3>\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
				</form>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title,
			html_title,
			html_checked[UDP_PORT==0], html_checked[UDP_PORT==1024], html_checked[UDP_PORT==3054], html_checked[UDP_PORT==49152],
			html_checked[DEVICE_NUM=='1'], html_checked[DEVICE_NUM=='2'], html_checked[DEVICE_NUM=='3'], html_checked[DEVICE_NUM=='4'], html_checked[DEVICE_NUM=='5'],
			AmbientChannelId, AmbientWriteKey,
			html_checked[SEND_INT_SEC==0], html_checked[SEND_INT_SEC==5], html_checked[SEND_INT_SEC==15], html_checked[SEND_INT_SEC==30], html_checked[SEND_INT_SEC==60]
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_reboot(){
	char s[HTML_INDEX_LEN_MAX];
	
	Serial.println("HTML reboot");
	snprintf(s, HTML_MISC_LEN_MAX,
		"<html>\
			<head>\
				<title>Wi-Fi 再起動中</title>\
				<meta http-equiv=\"refresh\" content=\"10;URL=http://%s/\">\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
			</head>\
			<body>\
				<h1>Wi-Fi 再起動中</h1>\
				<p>しばらくおまちください(約10秒)。</p>\
				<p>STAモードに切り替えたときは、LAN側からアクセスしてください。</p>\
			</body>\
		</html>", html_ip_s
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
	delay(110);
	server.close();
	TimerWakeUp_setSleepTime(2);
	TimerWakeUp_sleep();
}

void html_sleep(){
	char s[HTML_INDEX_LEN_MAX];
	
	Serial.println("HTML sleep");
	snprintf(s, HTML_MISC_LEN_MAX,
		"<html>\
			<head>\
				<title>Wi-Fi 電源OFF</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
			</head>\
			<body>\
				<h1>Wi-Fi ディープ・スリープへ移行中です。</h1>\
				<p>IO %d ピンをLowレベルに設定(BOOTボタン押下)すると復帰します。</p>\
				<p>復帰後のアクセス先＝<a href=\"http://%s/\">http://%s/</a></p>\
			</body>\
		</html>", PIN_SW, html_ip_s, html_ip_s
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
	delay(110);
	server.close();
	pinMode(PIN_SW,INPUT_PULLUP);
	while(!digitalRead(PIN_SW)){
		digitalWrite(PIN_LED,!digitalRead(PIN_LED));
		delay(50);
	}
	digitalWrite(PIN_LED,LOW);
	TimerWakeUp_setExternalInput((gpio_num_t)PIN_SW, LOW);
	TimerWakeUp_sleep();
}

void html_pinout(){
	char s[HTML_INDEX_LEN_MAX];
	char buf_s[128];
	int i;
	
	Serial.println("HTML pinout");
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s ピン配列表</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
			</head>\
			<body>\
				<h1>%s ピン配列表</h1>\
				<table><tr><th>番号</th><th>ピン名</th><th>接続先</th></tr>\
		", html_title, html_title
	);
				
	for(i=0;i<38;i++){
		Serial.print(" pin " + String(i) + " (" + html_PINOUT_S[i] + ") : " + html_PIN_ASSIGNED_S[i]);
		String S = "";
		if( html_PIN_ASSIGNED_S[i].length() == 0 ) S += "Null";
		else if( !(html_PIN_ASSIGNED_S[i].equals(html_PINOUT_S[i])) ) S += " ←接続";
		Serial.println(S);
		
		String("<tr><td>" + String(i)
			+ "</td><td>" + html_PINOUT_S[i]
			+ "</td><td>" + html_PIN_ASSIGNED_S[i] + S
			+ "</td></tr>"
		).toCharArray(buf_s, 128);
		strncat(s,buf_s, HTML_INDEX_LEN_MAX - strlen(s) - 1);
	}
	strncat(s,
		"		</table>\
				<hr>\
				<h4><a href =\"/\">戻る</a></h4>\
			</body>\
		</html>", HTML_INDEX_LEN_MAX - strlen(s) - 1
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_text(){
	server.send(200, "text/plain", "hello from esp8266!");
}

void html_demo(){
	char s[400];
	int sec = millis() / 1000;
	int min = sec / 60;
	int hr = min / 60;
	snprintf(s, 400,
		"<html>\
			<head>\
				<meta http-equiv='refresh' content='5'/>\
				<title>ESP32 Demo</title>\
				<style>\
					body { background-color: #cccccc; font-family: Arial, Helvetica, Sans-Serif; Color: #000088; }\
				</style>\
			</head>\
			<body>\
				<h1>Hello from ESP32!</h1>\
				<p>Uptime: %02d:%02d:%02d</p>\
				<img src=\"/test.svg\" />\
			</body>\
		</html>", hr, min % 60, sec % 60
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void drawGraph() {
	String out = "";
	char temp[100];
	out += "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"400\" height=\"150\">\n";
	out += "<rect width=\"400\" height=\"150\" fill=\"rgb(250, 230, 210)\" stroke-width=\"1\" stroke=\"rgb(0, 0, 0)\" />\n";
	out += "<g stroke=\"black\">\n";
	int y = rand() % 130;
	for (int x = 10; x < 390; x += 10) {
		int y2 = rand() % 130;
		sprintf(temp, "<line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" stroke-width=\"1\" />\n", x, 140 - y, x + 10, 140 - y2);
		out += temp;
		y = y2;
	}
	out += "</g>\n</svg>\n";
	server.send(200, "image/svg+xml", out);
}

void html_404(){
	String message = "File Not Found\n\n";
	message += "URI: ";
	message += server.uri();
	message += "\nMethod: ";
	message += (server.method() == HTTP_GET) ? "GET" : "POST";
	message += "\nArguments: ";
	message += server.args();
	message += "\n";
	for (uint8_t i = 0; i < server.args(); i++) {
		message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
	}
	server.send(404, "text/plain", message);
}

String html_ipAdrToString(uint32_t ip){
	String S = String(ip & 255) + ".";
	      S += String(ip>>8 & 255) + ".";
	      S += String(ip>>16 & 255) + ".";
	      S += String(ip>>24 & 255);
	return S;
}

void html_init(uint32_t ip, const char *domainName_local){
	html_ip=ip;
	if(MDNS_EN){
		snprintf(html_ip_s,16,"%s.local",
			domainName_local
		);
	}else{
		sprintf(html_ip_s,"%d.%d.%d.%d",
			ip & 255,
			ip>>8 & 255,
			ip>>16 & 255,
			ip>>24
		);
	}
	server.on("/", html_index);
	server.on("/wifi", html_wifi);
	server.on("/sensors", html_sensors);
	server.on("/pinout", html_pinout);
	server.on("/sendto", html_sendto);
	server.on("/reboot", html_reboot);
	server.on("/sleep", html_sleep);
//	server.on("/text", html_text);
//	server.on("/demo", html_demo);
//	server.on("/test.svg", drawGraph);
//	server.on("/inline", []() {
//		server.send(200, "text/plain", "this works as well");
//	});
	server.onNotFound(html_404);
	server.begin(); 						// サーバを起動する
}

void html_handleClient(){
	server.handleClient();
}
