#include <WiFiClient.h>
#include <WebServer.h>
#define html_title "IoT Sensor Core ESP32"
#define HTML_INDEX_LEN_MAX	4500
#define HTML_MISC_LEN_MAX	1024
#define HTML_RES_LEN_MAX	128

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
RTC_DATA_ATTR byte		BTN_EN=0;
RTC_DATA_ATTR boolean	PIR_EN=false;
RTC_DATA_ATTR boolean	AD_LUM_EN=false;
RTC_DATA_ATTR byte		AD_TEMP_EN=0;			// 1:LM61, 2:MCP9700
RTC_DATA_ATTR byte		I2C_HUM_EN=0;			// 1:SHT31, 2:Si7021
RTC_DATA_ATTR byte		I2C_ENV_EN=0;			// 1:BME280, 2:BMP280
RTC_DATA_ATTR boolean	I2C_ACCUM_EN=false;

*/

WebServer server(80);							// Webサーバ(ポート80=HTTP)定義

uint32_t html_ip=0;
char html_ip_s[16];

void html_index(){
	char s[HTML_INDEX_LEN_MAX];
	char res_s[HTML_RES_LEN_MAX]="待機中";
	char checked[2][18]={"","checked=\"checked\""};
	boolean sleep_b[5];
	int sleep_vals[5]={0,1,15,30,60};
	int adc_vals[6]={0,32,33,34,35,39};
	int i;
	
	Serial.println("HTML index");
	if(server.hasArg("SSID")){
		String S = server.arg("SSID");
		int len = S.length();
		if( len > 15 ){
			strcpy(res_s,"エラー：SSIDの文字数は15文字までです。");
		}else{
			if(server.hasArg("PASS")){
				String P = server.arg("PASS");
				len = P.length();
				if( len > 31 ){
					strcpy(res_s,"エラー：PASSの文字数は31文字までです。");
				}else{
					S.toCharArray(SSID_STA,16);
					P.toCharArray(PASS_STA,32);
					snprintf(res_s, HTML_RES_LEN_MAX,"SSIDを[%s]に設定しました(Wi-Fi再起動後に有効)。",SSID_STA);
					Serial.print(" SSID=");
					Serial.print(SSID_STA);
					Serial.print(" PASS=");
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

	if(server.hasArg("MODE")){
		String S = server.arg("MODE");
		i = S.toInt();
		if( i >= 1 && i <= 3 ){
			char mode_s[3][7]={"AP","STA","AP+STA"};
			WIFI_AP_MODE = i;
			snprintf(res_s, HTML_RES_LEN_MAX,"Wi-Fiモードを[%s]に設定しました(Wi-Fi再起動後に有効)。",mode_s[i-1]);
			Serial.print(" WIFI_AP_MODE=");
			Serial.println(WIFI_AP_MODE);
		}else strcpy(res_s,"エラー：Wi-Fiモードの設定値が範囲外です。");
	}
	
	if(server.hasArg("SLEEP")){
		String S = server.arg("SLEEP");
		int sleep_i = S.toInt();
		for(i=0; i<5; i++){
			if( sleep_i == sleep_vals[i]){
				SLEEP_SEC = sleep_vals[i] * 60 - 5;
				snprintf(res_s, HTML_RES_LEN_MAX,"間欠動作間隔を[%d]分に設定しました。スリープ中は操作できません。",sleep_i);
				Serial.print(" SLEEP_SEC=");
				Serial.println(SLEEP_SEC);
				break;
			}
		}
		if(i==5) strcpy(res_s,"エラー：間欠動作間隔の設定値が範囲外です。");
	}
	for(i=0;i<5;i++){
		if( (SLEEP_SEC + 5) / 60 == sleep_vals[i] ) sleep_b[i]=true;
		else sleep_b[i]=false;
	}
	
	if(server.hasArg("TEMP_EN")){
		String S = server.arg("TEMP_EN");
		i = S.toInt();
		if( i==0 ) TEMP_EN=false;
		if( i==1 ) TEMP_EN=true;
		Serial.print(" TEMP_EN=");
		Serial.println(TEMP_EN);
	}
	if(server.hasArg("HALL_EN")){
		String S = server.arg("HALL_EN");
		i = S.toInt();
		if( i==0 ) HALL_EN=false;
		if( i==1 ) HALL_EN=true;
		Serial.print(" HALL_EN=");
		Serial.println(HALL_EN);
	}
	if(server.hasArg("ADC_EN")){
		String S = server.arg("ADC_EN");
		int adc = S.toInt();
		for(i=0;i<6;i++) if(adc == adc_vals[i]) ADC_EN=adc;
		Serial.print(" ADC_EN=");
		Serial.println(ADC_EN);
	}
	if(server.hasArg("BTN_EN")){
		String S = server.arg("BTN_EN");
		i = S.toInt();
		if( i >= 0 && i <= 2) BTN_EN=i;
		Serial.print(" BTN_EN=");
		Serial.println(BTN_EN);
	}
	if(server.hasArg("PIR_EN")){
		String S = server.arg("PIR_EN");
		i = S.toInt();
		if( i==0 ) PIR_EN=false;
		if( i==1 ) PIR_EN=true;
		Serial.print(" PIR_EN=");
		Serial.println(PIR_EN);
	}
	if(server.hasArg("AD_LUM_EN")){
		String S = server.arg("AD_LUM_EN");
		i = S.toInt();
		if( i==0 ) AD_LUM_EN=false;
		if( i==1 ) AD_LUM_EN=true;
		Serial.print(" AD_LUM_EN=");
		Serial.println(AD_LUM_EN);
	}
	if(server.hasArg("AD_TEMP_EN")){
		String S = server.arg("AD_TEMP_EN");
		i = S.toInt();
		if( i >= 0 && i <= 2) AD_TEMP_EN=i;
		Serial.print(" AD_TEMP_EN=");
		Serial.println(AD_TEMP_EN);
	}
	if(server.hasArg("I2C_HUM_EN")){
		String S = server.arg("I2C_HUM_EN");
		i = S.toInt();
		if( i >= 0 && i <= 2) I2C_HUM_EN=i;
		Serial.print(" I2C_HUM_EN=");
		Serial.println(I2C_HUM_EN);
	}
	if(server.hasArg("I2C_ENV_EN")){
		String S = server.arg("I2C_ENV_EN");
		i = S.toInt();
		if( i >= 0 && i <= 2) I2C_ENV_EN=i;
		Serial.print(" I2C_ENV_EN=");
		Serial.println(I2C_ENV_EN);
	}
	if(server.hasArg("I2C_ACCUM_EN")){
		String S = server.arg("I2C_ACCUM_EN");
		i = S.toInt();
		if( i==0 ) I2C_ACCUM_EN=false;
		if( i==1 ) I2C_ACCUM_EN=true;
		Serial.print(" I2C_ACCUM_EN=");
		Serial.println(I2C_ACCUM_EN);
	}
	if(server.hasArg("SENSORS")){
		String S = sensors_get();
		strcpy(res_s,"センサ取得値=");
		int len=strlen(res_s);
		S.toCharArray(&res_s[len],HTML_RES_LEN_MAX-len);
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
					<p>%s</>\
				<hr>\
				<h3>Wi-Fi 設定</h3>\
				<form method=\"GET\" action=\"http://%s/\">\
					<p>動作モード　\
					<input type=\"radio\" name=\"MODE\" value=\"1\" %s>AP\
					<input type=\"radio\" name=\"MODE\" value=\"2\" %s>STA\
					<input type=\"radio\" name=\"MODE\" value=\"3\" %s>AP+STA\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
					</p>\
				</form>\
				<form method=\"GET\" action=\"http://%s/\">\
					<p>STA接続先　\
					SSID=<input type=\"text\" name=\"SSID\" value=\"%s\" size=\"15\">\
					PASS=<input type=\"password\" name=\"PASS\" size=\"15\">\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
					</p>\
				</form>\
				<form method=\"GET\" action=\"http://%s/reboot\">\
					<p>Wi-Fi再起動　\
					<input type=\"submit\" name=\"BOOT\" value=\"実行\" size=\"4\">\
					</p>\
					<p>Wi-Fiモードを[STA]にすると無線LANが切断されます(操作不可になる)</p>\
					<p>[AP]:本機がAPとして動作, [STA]:他のAPへ接続, [AP+STA]:両方</p>\
				</form>\
				<hr>\
				<h3>スリープ設定</h3>\
				<form method=\"GET\" action=\"http://%s/\">\
					<p>間欠動作　\
					<input type=\"radio\" name=\"SLEEP\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"SLEEP\" value=\"1\" %s>1分\
					<input type=\"radio\" name=\"SLEEP\" value=\"15\" %s>15分\
					<input type=\"radio\" name=\"SLEEP\" value=\"30\" %s>30分\
					<input type=\"radio\" name=\"SLEEP\" value=\"60\" %s>60分\
					<input type=\"submit\" value=\"設定\" size=\"4\">\
					</p>\
					<p>[OFF]以外に設定するとスリープ中(殆どの時間)は操作できません。</p>\
				</form>\
				<hr>\
				<h3>センサ設定</h3>\
				<form method=\"GET\" action=\"http://%s/\">\
					<p>内蔵温度センサ　\
					<input type=\"radio\" name=\"TEMP_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"TEMP_EN\" value=\"1\" %s>ON\
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
					<input type=\"radio\" name=\"ADC_EN\" value=\"39\" %s>IO39\
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
					<p>設定を送信　\
					<input type=\"submit\" name=\"SENSORS\" value=\"設定\" size=\"4\">\
					</p>\
				</form>\
				<form method=\"GET\" action=\"http://%s/\">\
					<p>センサ値を取得　\
					<input type=\"submit\" name=\"SENSORS\" value=\"取得\" size=\"4\">\
					</p>\
				</form>\
				<hr>\
				<p>by <a href=\"http://bokunimo.net/\">http://bokunimo.net/</a></p>\
			</body>\
		</html>", html_title,
			html_title, res_s,
			html_ip_s, checked[WIFI_AP_MODE==1], checked[WIFI_AP_MODE==2], checked[WIFI_AP_MODE==3],
			html_ip_s, SSID_STA,
			html_ip_s,
			html_ip_s, checked[sleep_b[0]], checked[sleep_b[1]], checked[sleep_b[2]], checked[sleep_b[3]], checked[sleep_b[4]],
			html_ip_s,
				checked[!TEMP_EN], checked[TEMP_EN], 
				checked[!HALL_EN], checked[HALL_EN], 
				checked[ADC_EN==0], checked[ADC_EN==32], checked[ADC_EN==33], checked[ADC_EN==34], checked[ADC_EN==35], checked[ADC_EN==39],
				checked[BTN_EN==0], checked[BTN_EN==1], checked[BTN_EN==2],
				checked[PIR_EN==0], checked[PIR_EN==1],
				checked[AD_LUM_EN==0], checked[AD_LUM_EN==1],
				checked[AD_TEMP_EN==0], checked[AD_TEMP_EN==1], checked[AD_TEMP_EN==2],
				checked[I2C_HUM_EN==0], checked[I2C_HUM_EN==1], checked[I2C_HUM_EN==2],
				checked[I2C_ENV_EN==0], checked[I2C_ENV_EN==1], checked[I2C_ENV_EN==2],
				checked[I2C_ACCUM_EN==0], checked[I2C_ACCUM_EN==1],
			html_ip_s
	);
	server.send(200, "text/html", s);
	Serial.print("done, ");
	Serial.print(strlen(s));
	Serial.println(" bytes");
	if(HTML_INDEX_LEN_MAX - 1 <= strlen(s)) Serial.println("ERROR: Prevented Buffer Overrun");
}

void html_reboot(){
	char s[HTML_MISC_LEN_MAX];
	
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
				<p>しばらくおまちください。</p>\
				<p>STAモードに切り替えたときは、LAN側からアクセスしてください。</p>\
			</body>\
		</html>", html_ip_s
	);
	server.send(200, "text/html", s);
	Serial.print("done, ");
	Serial.print(strlen(s));
	Serial.println(" bytes");
	if(HTML_MISC_LEN_MAX - 1 <= strlen(s)) Serial.println("ERROR: Prevented Buffer Overrun");
	delay(110);
	server.close();
	TimerWakeUp_setSleepTime(2);
	TimerWakeUp_sleep();
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
	Serial.print("done, ");
	Serial.print(strlen(s));
	Serial.println(" bytes");
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

void html_init(uint32_t ip){
	html_ip=ip;
	sprintf(html_ip_s,"%d.%d.%d.%d",
		ip & 255,
		ip>>8 & 255,
		ip>>16 & 255,
		ip>>24
	);
	server.on("/", html_index);
	server.on("/reboot", html_reboot);
	server.on("/text", html_text);
	server.on("/demo", html_demo);
	server.on("/test.svg", drawGraph);
	server.on("/inline", []() {
		server.send(200, "text/plain", "this works as well");
	});
	server.onNotFound(html_404);
	server.begin(); 						// サーバを起動する
}

void html_handleClient(){
	server.handleClient();
}
