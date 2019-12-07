#include <WiFiClient.h>
#include <WebServer.h>
#define html_title "IoT Sensor Core ESP32"
#define HTML_INDEX_LEN_MAX	4096
#define HTML_MISC_LEN_MAX	1024
#define HTML_RES_LEN_MAX	256
#define HTML_S_LEN_MAX		96
#define HTML_ERROR_LEN_MAX	64

// extern RTC_DATA_ATTR
// extern File file
// extern FILENAME

WebServer server(80);							// Webサーバ(ポート80=HTTP)定義

int32_t 	ip_num_ap;
int32_t 	ip_num_sta;
char 		html_ip_ui_s[16];
char 		html_ip_num_s[16];
char 		html_ip_mdns_s[16];
char 		html_error_s[HTML_ERROR_LEN_MAX]="";
const char	html_checked[2][18]={"","checked=\"checked\""};

void html_error(const char *err, const char *html, const char *lcd){
	int len = HTML_ERROR_LEN_MAX - strlen(html_error_s) - 5;
	if( len > 0 ){
		if( strlen(html) > 0){
			strncat(html_error_s, html, len);
		}else{
			strncat(html_error_s, err, len);
		}
		strcat(html_error_s,"<br>");
	}else Serial.println("ERROR: html_error Buffer Overrun");
	Serial.print("ERROR: ");
	Serial.println(err);
	if(LCD_EN && strlen(lcd) > 0){
		i2c_lcd_print("ERROR!");
		i2c_lcd_print2(lcd);
	}
}

void html_error(const char *err, const char *html){
	html_error(err, html, "");
}

boolean html_check_overrun(int len){
	Serial.print("done html, ");
	Serial.print(len);
	Serial.println(" bytes");
	if(HTML_INDEX_LEN_MAX - 256 < len){
		Serial.print("WARNING: No Enough Buffer. Limit=");
		Serial.print(HTML_INDEX_LEN_MAX);
	}
	if(HTML_INDEX_LEN_MAX - 1 <= len){
		Serial.println("ERROR: Prevented HTML_INDEX Buffer Overrun");
		return false;
	}
	return true;
}

void _html_cat_res_s(char *res_s, const char *s){
	if( strlen(html_error_s) > 0 ){
		strncpy(res_s, html_error_s, HTML_RES_LEN_MAX - 7);
		memset(html_error_s,'\0',HTML_ERROR_LEN_MAX);
	}
	if( strlen(res_s) >= HTML_RES_LEN_MAX - 8 ){
		Serial.println("ERROR: Prevented HTML_RES Buffer Overrun");
		return;
	}
	if( strlen(s) >= HTML_S_LEN_MAX ){
		Serial.println("WARNING: No Enough HTML_S Buffer");
	}
	int len = HTML_RES_LEN_MAX - strlen(res_s) - 5;
	if( strlen(s) > 0 && len > 0){
		strncat(res_s, s, len);
		strcat(res_s,"<br>");
	}
}

void _html_cat_res_s(char *res_s){
	_html_cat_res_s(res_s, "");
}

void html_dataAttrSet(char *res_s){
	int i;
	char s[HTML_S_LEN_MAX];
	
	if(server.hasArg("WIFI_AP_MODE")){
		String S = server.arg("WIFI_AP_MODE");
		i = S.toInt();
		if( i >= 1 && i <= 3 && WIFI_AP_MODE != i ){
			char mode_s[3][7]={"AP","STA","AP+STA"};
			WIFI_AP_MODE = i;
			snprintf(s, HTML_S_LEN_MAX,"Wi-Fiモードを[%s]に設定しました(要Wi-Fi再起動)",mode_s[i-1]);
			_html_cat_res_s(res_s, s);
			Serial.print(" WIFI_AP_MODE=");
			Serial.println(WIFI_AP_MODE);
		}
	}
	if(server.hasArg("MDNS_EN")){
		String S = server.arg("MDNS_EN");
		i = S.toInt();
		if( i >= 0 && i <= 1 ){
			MDNS_EN = (boolean)i;
			char mode_s[2][4]={"OFF","ON"};
			snprintf(s, HTML_S_LEN_MAX,"mDNSを[%s]に設定しました(要Wi-Fi再起動)",mode_s[i]);
			_html_cat_res_s(res_s, s);
			Serial.print(" MDNS_EN=");
			Serial.println(MDNS_EN);
		}
	}
	/*
	if(MDNS_EN && WIFI_AP_MODE == 3){
		strcpy(html_ip_ui_s,html_ip_mdns_s);
	}else{
		strcpy(html_ip_ui_s,html_ip_num_s);
	}
	*/
	if(server.hasArg("WPS_STA")){
		String S = server.arg("WPS_STA");
		i = S.toInt();
		if( i == 0 ) WPS_STA = false;
		if( i == 1 ){
			WPS_STA = true;
			snprintf(s, HTML_S_LEN_MAX,"WPSを設定しました(Wi-Fi再起動後[%d]秒以内有効)",TIMEOUT /1000);
			_html_cat_res_s(res_s, s);
			if((WIFI_AP_MODE & 2) != 2){
				WIFI_AP_MODE |= 2;
				_html_cat_res_s(res_s, "Wi-Fiモード(STA)を設定しました");
				Serial.print(" WIFI_AP_MODE=");
				Serial.println(WIFI_AP_MODE);
			}
		}
		Serial.print(" WPS_STA=");
		Serial.println(WPS_STA);
	}
	
	if(server.hasArg("SSID_STA")){
		String S = server.arg("SSID_STA");
		int len = S.length();
		if( len > 16 ){
			_html_cat_res_s(res_s,"ERROR:接続先SSIDは16文字までです");
		}else if( len > 0 ){
			if(WPS_STA){
				_html_cat_res_s(res_s,"新しいSSIDはWPSによって設定されます");
			}else if(server.hasArg("PASS_STA")){
				String P = server.arg("PASS_STA");
				len = P.length();
				if( len > 64 ){
					_html_cat_res_s(res_s,"ERROR:接続先PASSは64文字までです");
				}else if( len > 0 ){
					S.toCharArray(SSID_STA,16);
					P.toCharArray(PASS_STA,32);
					snprintf(s, HTML_S_LEN_MAX,"接続先SSIDを[%s]に設定しました(要Wi-Fi再起動)",SSID_STA);
					_html_cat_res_s(res_s, s);
					Serial.print(" SSID_STA=");
					Serial.print(SSID_STA);
					Serial.print(" PASS_STA=");
					Serial.println(PASS_STA);
					if((WIFI_AP_MODE & 2) != 2){
						WIFI_AP_MODE |= 2;
						_html_cat_res_s(res_s, "Wi-Fiモード(STA)を設定しました(同上)");
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
			_html_cat_res_s(res_s,"ERROR:本機SSIDは15文字までです");
		}else if( len > 0 ){
			if(server.hasArg("PASS_AP")){
				String P = server.arg("PASS_AP");
				len = P.length();
				if( len > 15 ){
					_html_cat_res_s(res_s,"ERROR:本機PASSは15文字までです");
				}else{
					S.toCharArray(SSID_AP,16);
					P.toCharArray(PASS_AP,16);
					snprintf(s, HTML_S_LEN_MAX,"本機SSIDを[%s]に設定しました(要Wi-Fi再起動)",SSID_AP);
					_html_cat_res_s(res_s, s);
					Serial.print(" SSID_AP=");
					Serial.print(SSID_AP);
					Serial.print(" PASS_AP=");
					Serial.println(PASS_AP);
				}
			}
		}
	}
	if(server.hasArg("SLEEP_SEC")){
		int sleep_i = server.arg("SLEEP_SEC").toInt();
		if(sleep_i >=0 && sleep_i <= 65535 && sleep_i != SLEEP_SEC){
			SLEEP_SEC = sleep_i;
			if(SLEEP_SEC == 65535 )	_html_cat_res_s(res_s, "スリープを[ON]に設定しました");
			else if(SLEEP_SEC == 0)	_html_cat_res_s(res_s, "スリープを[OFF]に設定しました");
			else {
				snprintf(s, HTML_S_LEN_MAX,"間欠動作間隔を[%d]分[%d]秒に設定しました",(sleep_i+5)/60,(sleep_i+5)%60);
				_html_cat_res_s(res_s, s);
			}
			Serial.print(" SLEEP_SEC=");
			Serial.println(SLEEP_SEC);
		}
	}
	
	if(server.hasArg("BOARD_TYPE")){
		i = server.arg("BOARD_TYPE").toInt();
		if( i >= 0 && i < sensors_board_types_num() ){
			if( i != BOARD_TYPE ){
				BOARD_TYPE = i;
				snprintf(s, HTML_S_LEN_MAX,"ボードを[%s]に設定しました",sensors_boardName(i));
				_html_cat_res_s(res_s, s);
				sensors_init();
			}
			Serial.print(" BOARD_TYPE=");
			Serial.println(BOARD_TYPE);
		}
	}
	if(server.hasArg("PIN_LED")){
		int prev = PIN_LED;
		i = server.arg("PIN_LED").toInt();
		if( !sensors_init_LED(i) || (i!=2 && i!=4 && i!=22 && i!=23) ){
			_html_cat_res_s(res_s, "LEDの設定に失敗しました");
		}else if( i != prev ){
			snprintf(s, HTML_S_LEN_MAX,"LEDピンを[IO%d]に設定しました",i);
			_html_cat_res_s(res_s, s);
		}
		Serial.print(" PIN_LED=");
		Serial.println(PIN_LED);
	}
	if(server.hasArg("LED")){
		i = server.arg("LED").toInt();
		if( i != digitalRead(PIN_LED) ){
			digitalWrite(PIN_LED,i);
			Serial.print(" LED=");
			Serial.println(i%2);
			snprintf(s, HTML_S_LEN_MAX,"LEDを[%d]に設定しました",i%2);
			_html_cat_res_s(res_s, s);
		}
	}
	if(server.hasArg("LCD_EN")){
		i = server.arg("LCD_EN").toInt();
		if( !sensors_init_LCD(i) ){
			_html_cat_res_s(res_s, "I2C LCDの設定に失敗しました");
		}
		Serial.print(" LCD_EN=");
		Serial.println(LCD_EN);
	}
	if(server.hasArg("DISPLAY")){
		if(LCD_EN > 0){
			String S = server.arg("DISPLAY");
			i2c_lcd_print_S( &S );
			Serial.println(" DISPLAY=" + S);
		}
	}
	if(server.hasArg("TEMP_EN")){
		sensors_init_TEMP( server.arg("TEMP_EN").toInt() );
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
		sensors_init_HALL( server.arg("HALL_EN").toInt() );
		Serial.print(" HALL_EN=");
		Serial.println(HALL_EN);
	}
	if(server.hasArg("ADC_EN")){
		sensors_init_ADC( server.arg("ADC_EN").toInt() );
		Serial.print(" ADC_EN=");
		Serial.println(ADC_EN);
	}
	if(server.hasArg("BTN_EN")){
		sensors_init_BTN( server.arg("BTN_EN").toInt() );
		Serial.print(" BTN_EN=");
		Serial.println(BTN_EN);
	}
	if(server.hasArg("PIR_EN")){
		if( !sensors_init_PIR( server.arg("PIR_EN").toInt()) ){
			_html_cat_res_s(res_s, "人感センサの設定に失敗しました");
		}
		Serial.print(" PIR_EN=");
		Serial.println(PIR_EN);
	}
	if(server.hasArg("IR_IN_EN")){
		if( !sensors_init_IR_IN( server.arg("IR_IN_EN").toInt()) ){
			_html_cat_res_s(res_s, "赤外線リモコンレシーバの設定に失敗しました");
		}
		Serial.print(" IR_IN_EN=");
		Serial.println(IR_IN_EN);
	}
	if(server.hasArg("AD_LUM_EN")){
		if( !sensors_init_AD_LUM( server.arg("AD_LUM_EN").toInt()) ){
			_html_cat_res_s(res_s, "照度センサの設定に失敗しました");
		}
		Serial.print(" AD_LUM_EN=");
		Serial.println(AD_LUM_EN);
	}
	if(server.hasArg("AD_TEMP_EN")){
		if( !sensors_init_AD_TEMP(server.arg("AD_TEMP_EN").toInt()) ){
			_html_cat_res_s(res_s, "温度センサの設定に失敗しました");
		}
		Serial.print(" AD_TEMP_EN=");
		Serial.println(AD_TEMP_EN);
	}
	if(server.hasArg("I2C_HUM_EN")){
		i = server.arg("I2C_HUM_EN").toInt();
		if( i > 0 && i != I2C_HUM_EN && sensors_wireBegin()) snprintf(res_s, HTML_RES_LEN_MAX,"(警告)既にI2Cが起動しています");
		if( !sensors_init_I2C_HUM(i) ){
			_html_cat_res_s(res_s, "I2C温湿度センサの設定に失敗しました");
		}
		Serial.print(" I2C_HUM_EN=");
		Serial.println(I2C_HUM_EN);
	}
	if(server.hasArg("I2C_ENV_EN")){
		i = server.arg("I2C_ENV_EN").toInt();
		if( i > 0 && i != I2C_ENV_EN && sensors_wireBegin()) snprintf(res_s, HTML_RES_LEN_MAX,"(警告)既にI2Cが起動しています");
		if( !sensors_init_I2C_ENV(i) ){
			_html_cat_res_s(res_s, "I2C環境センサの設定に失敗しました");
		}
		Serial.print(" I2C_ENV_EN=");
		Serial.println(I2C_ENV_EN);
	}
	if(server.hasArg("I2C_ACCEM_EN")){
		i = server.arg("I2C_ACCEM_EN").toInt();
		if( i > 0 && i != I2C_ACCEM_EN && sensors_wireBegin()) snprintf(res_s, HTML_RES_LEN_MAX,"(警告)既にI2Cが起動しています");
		if( !sensors_init_I2C_ACCEM(i) ){
			_html_cat_res_s(res_s, "I2C加速度センサの設定に失敗しました");
		}
		Serial.print(" I2C_ACCEM_EN=");
		Serial.println(I2C_ACCEM_EN);
	}
	if(server.hasArg("TIMER_EN")){
		i = server.arg("TIMER_EN").toInt();
		if( i < 0 || i > 1 ){
			_html_cat_res_s(res_s, "動作時間測定の設定に失敗しました");
		}else TIMER_EN = (boolean)i;
		Serial.print(" TIMER_EN=");
		Serial.println(TIMER_EN);
	}
	if(server.hasArg("DEVICE_NUM")){
		i = server.arg("DEVICE_NUM").toInt();
		if( i >= 0 && i <= 9 ){
			char c = (char)((int)'0'+i);
			if( DEVICE_NUM != c ){
				snprintf(s, HTML_S_LEN_MAX,"デバイス番号を[%c]に設定しました",c);
				_html_cat_res_s(res_s, s);
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
			if(i){
				snprintf(s, HTML_S_LEN_MAX,"UDP送信ポート番号を[%d]に設定しました",i);
				_html_cat_res_s(res_s, s);
			}
			else _html_cat_res_s(res_s, "UDP送信を[OFF]に設定しました");
			Serial.print(" UDP_PORT=");
			Serial.println(UDP_PORT);
		}
	}
	if(server.hasArg("UDP_MODE")){
		i = server.arg("UDP_MODE").toInt();
		if( i >= 0 && i <= 3 && UDP_MODE != i){
			UDP_MODE = i;
			if(i) _html_cat_res_s(res_s, "UDP送信モードを変更しました");
			Serial.print(" UDP_MODE=");
			Serial.println(UDP_MODE);
		}
	}
	if(server.hasArg("AmbientChannelId")){
		int i = server.arg("AmbientChannelId").toInt();
		if( i != AmbientChannelId){
			AmbientChannelId = i;
			if(i){
				snprintf(s, HTML_S_LEN_MAX,"Ambient ID を[%d]に設定しました",i);
				_html_cat_res_s(res_s, s);
			} else _html_cat_res_s(res_s, "Ambientへの送信を[OFF]にしました");
			Serial.print(" AmbientChannelId=");
			Serial.println(AmbientChannelId);
		}
	}
	if(server.hasArg("AmbientWriteKey")){
		String S = server.arg("AmbientWriteKey");
		if( S.length() == 16 && S.equals(String(AmbientWriteKey)) == false ){
			S.toCharArray(AmbientWriteKey,17);
			snprintf(s, HTML_S_LEN_MAX,"Ambient(ID=%d)のWriteKeyを[%s]に設定しました",AmbientChannelId,AmbientWriteKey);
			_html_cat_res_s(res_s, s);
		}
		Serial.print(" AmbientWriteKey=");
		Serial.println(AmbientWriteKey);
	}
	if(server.hasArg("SEND_INT_SEC")){
		i = server.arg("SEND_INT_SEC").toInt();
		if( SEND_INT_SEC != i){
			SEND_INT_SEC = i;
			if(i){
				snprintf(s, HTML_S_LEN_MAX,"自動送信間隔(動作時)を[%d]に設定しました",i);
				_html_cat_res_s(res_s, s);
			} else _html_cat_res_s(res_s, "自動送信を[OFF]に設定しました");
			Serial.print(" SEND_INT_SEC=");
			Serial.println(SEND_INT_SEC);
		}
	}
}

void html_index(){
	char s[HTML_INDEX_LEN_MAX];
	char res_s[HTML_RES_LEN_MAX]="待機中";
	char sensors_res_s[HTML_RES_LEN_MAX]="なし";
	char sensors_s[HTML_RES_LEN_MAX]="";
	
	/////////////// ----------------------
	Serial.println("HTML index -----------");
	
	_html_cat_res_s(res_s);
	html_dataAttrSet(res_s);
	if(server.hasArg("SENSORS")){
		/*
		strcpy(sensors_res_s,"センサ取得値=");
		int len=strlen(sensors_res_s);
		String payload = String(sensors_get());
		payload.toCharArray(&sensors_res_s[len],HTML_RES_LEN_MAX-len);
		*/
		String payload = String(sensors_get());
		payload.toCharArray(sensors_res_s,HTML_RES_LEN_MAX);
	}
	sensors_name().toCharArray(sensors_s,HTML_RES_LEN_MAX);
	
	char mode_s[4][7]={"OFF","AP","STA","AP+STA"};
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>%s</h1>Ver.%s &emsp; mode=%s &emsp; IP=%s\
				<hr>\
				<h3>状態</h3>\
					<p>%s</p>\
				<h3>取得したセンサ値</h3>\
					<p>値=%s</p><p>項目=%s</p>\
				<h3>センサ値の取得指示</h3>\
					<p><a href=\"http://%s/?SENSORS=GET\">http://%s/?SENSORS=GET</a>\
					<form method=\"GET\" action=\"/\">\
					<input type=\"submit\" name=\"SENSORS\" value=\"取得\">\
					</form></p>\
				<hr>\
				<h3>設定</h3>\
				<h4><a href=\"wifi\">Wi-Fi 設定</a></h4>\
				<h4><a href=\"sensors\">センサ入力設定</a></h4>\
				<h4><a href=\"display\">表示出力設定</a></h4>\
				<h4><a href=\"pinout\">ピン配列表</a></h4>\
				<h4><a href=\"sendto\">データ送信設定</a></h4>\
				<h4><a href=\"format\">SPIFFS初期化</a></h4>\
				<hr>\
				<h3>電源</h3>\
				<h4><a href=\"reboot\">Wi-Fi 再起動</a>(Wi-FiとGPIO を再設定)</h4>\
				<h4><a href=\"gpio_init\">GPIO 再起動</a>(GPIO のみ再設定)</h4>\
				<h4><a href=\"sleep\">ESP32 OFF</a>(設定を保持したままスリープ)</h4>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title, html_title,VERSION, mode_s[WIFI_AP_MODE], html_ip_num_s, res_s, sensors_res_s, sensors_s, html_ip_ui_s, html_ip_ui_s
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_wifi(){
	char s[HTML_INDEX_LEN_MAX];
	char res_s[HTML_RES_LEN_MAX]="";
	int i;
	
	/////////////// ----------------------
	Serial.println("HTML Wi-Fi -----------");
	
	_html_cat_res_s(res_s);
	html_dataAttrSet(res_s);
	
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s Wi-Fi 設定</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>%s Wi-Fi 設定</h1>\
				<p>%s</p>\
				<hr>\
				<h3>Wi-Fi 動作モード</h3>\
				<form method=\"GET\" action=\"/wifi\">\
					<input type=\"radio\" name=\"WIFI_AP_MODE\" value=\"1\" %s>AP\
					<input type=\"radio\" name=\"WIFI_AP_MODE\" value=\"2\" %s>STA\
					<input type=\"radio\" name=\"WIFI_AP_MODE\" value=\"3\" %s>AP+STA\
					<p><input type=\"submit\" value=\"設定\"></p>\
					<p>Wi-Fiモードを[STA]にすると本機の無線APが停止します</p>\
					<p>[AP]:本機がAPとして動作, [STA]:他のAPへ接続, [AP+STA]:両方</p>\
				</form>\
				<hr>\
				<h3>mDNS(Bonjour)モード</h3>\
				<form method=\"GET\" action=\"/wifi\">\
					<input type=\"radio\" name=\"MDNS_EN\" value=\"1\" %s>ON\
					<input type=\"radio\" name=\"MDNS_EN\" value=\"0\" %s>OFF\
					<p><input type=\"submit\" value=\"設定\"></p>\
					<p>iOS,Windows 10,macOSの場合は[ON],その他は[OFF]を設定して下さい</p>\
				</form>\
				<hr>\
				<h3>Wi-Fi AP 設定</h3>\
				<form method=\"GET\" action=\"/wifi\">\
					<p>本機 Wi-Fi AP(アクセスポイント)へ接続するための設定です</p>\
					SSID=<input type=\"text\" name=\"SSID_AP\" value=\"%s\" size=\"10\">\
					PASS=<input type=\"password\" name=\"PASS_AP\" value=\"%s\" size=\"10\">\
					<p><input type=\"submit\" value=\"設定\"></p>\
					<p>変更すると,Wi-Fi を新しい設定で再接続する必要があります</p>\
				</form>\
				<hr>\
				<h3>Wi-Fi STA 接続先</h3>\
				<form method=\"GET\" action=\"/wifi\">\
					<p>お手持ちのWi-Fiアクセスポイントの設定を記入し[設定]を押してください</p>\
					<input type=\"radio\" name=\"WPS_STA\" value=\"1\" %s>WPS\
					<input type=\"radio\" name=\"WPS_STA\" value=\"0\" %s>\
					SSID=<input type=\"text\" name=\"SSID_STA\" value=\"%s\" size=\"10\">\
					PASS=<input type=\"password\" name=\"PASS_STA\" size=\"10\">\
					<p><input type=\"submit\" value=\"設定\"></p>\
				</form>\
				<hr>\
				<h3>Wi-Fi 再起動</h3>\
				<form method=\"GET\" action=\"/reboot\">\
					<p>Wi-Fi 設定を有効にするには再起動を行ってください</p>\
					<p>\
						<input type=\"submit\" name=\"BOOT\" value=\"再起動\">\
						<input type=\"submit\" name=\"SAVE\" value=\"保存\">(Wi-Fi設定を保存)\
					</p>\
				</form>\
				<hr>\
				<br><br><h3>スリープ設定</h3>\
				<form method=\"GET\" action=\"/\">\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"25\" %s>30秒\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"55\" %s>1分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"175\" %s>3分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"595\" %s>10分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"1795\" %s>30分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"3595\" %s>60分\
					<input type=\"radio\" name=\"SLEEP_SEC\" value=\"65535\" %s>∞\
					<p><input type=\"submit\" value=\"設定\"></p>\
					<p>[OFF]以外に設定するとスリープ中に操作できなくなります</p>\
				</form>\
				<hr>\
				<form method=\"GET\" action=\"/\">\
					<p><input type=\"submit\" name=\"SENSORS\" value=\"前の画面に戻る\"></p>\
				</form>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title,
			html_title,  res_s,
			html_checked[WIFI_AP_MODE==1], html_checked[WIFI_AP_MODE==2], html_checked[WIFI_AP_MODE==3],
			html_checked[MDNS_EN==1], html_checked[MDNS_EN==0], 
			SSID_AP, PASS_AP,
			html_checked[WPS_STA==true],html_checked[WPS_STA==false],SSID_STA,
			html_checked[SLEEP_SEC==0], html_checked[SLEEP_SEC==25], html_checked[SLEEP_SEC==55], html_checked[SLEEP_SEC==175],
			html_checked[SLEEP_SEC==595], html_checked[SLEEP_SEC==1795], html_checked[SLEEP_SEC==3595], html_checked[SLEEP_SEC==65535]
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_sensors(){
	char s[HTML_INDEX_LEN_MAX];
	
	/////////////// ----------------------
	Serial.println("HTML sensors ---------");
	
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s センサ入力設定</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>%s センサ入力設定</h1>\
				<form method=\"GET\" action=\"/\">\
					<p>ボード　\
					<input type=\"radio\" name=\"BOARD_TYPE\" value=\"0\" %s>ESP\
					<input type=\"radio\" name=\"BOARD_TYPE\" value=\"1\" %s>DevKitC\
					<input type=\"radio\" name=\"BOARD_TYPE\" value=\"2\" %s>TTGO Koala\
					</p>\
					<hr>\
					<p>内蔵温度センサ　\
					<input type=\"radio\" name=\"TEMP_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"TEMP_EN\" value=\"1\" %s>ON\
					補正値=<input type=\"text\" name=\"TEMP_ADJ\" value=\"%d\" size=\"5\">℃\
					</p>\
					<p>内蔵磁気センサ　\
					<input type=\"radio\" name=\"HALL_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"HALL_EN\" value=\"1\" %s>ON\
					</p>\
					<p>ADC　\
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
					<p>赤外線RC　\
					<input type=\"radio\" name=\"IR_IN_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"IR_IN_EN\" value=\"1\" %s>AEHA\
					<input type=\"radio\" name=\"IR_IN_EN\" value=\"2\" %s>NEC\
					<input type=\"radio\" name=\"IR_IN_EN\" value=\"3\" %s>SIRC\
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
					<p>　　　　　　　\
					<input type=\"radio\" name=\"I2C_HUM_EN\" value=\"3\" %s>AM23<u>20</u>\
					<input type=\"radio\" name=\"I2C_HUM_EN\" value=\"4\" %s>AM23<u>02</u>\
					<input type=\"radio\" name=\"I2C_HUM_EN\" value=\"5\" %s>DHT11\
					</p>\
					<p>環境センサ　\
					<input type=\"radio\" name=\"I2C_ENV_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"I2C_ENV_EN\" value=\"1\" %s>BME280\
					<input type=\"radio\" name=\"I2C_ENV_EN\" value=\"2\" %s>BMP280\
					</p>\
					<p>加速度センサ　\
					<input type=\"radio\" name=\"I2C_ACCEM_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"I2C_ACCEM_EN\" value=\"1\" %s>ADXL345\
					</p>\
					<p>動作時間測定　\
					<input type=\"radio\" name=\"TIMER_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"TIMER_EN\" value=\"1\" %s>ON\
					</p>\
					<p><input type=\"submit\" name=\"SENSORS\" value=\"設定\">(センサ設定の実行)</p>\
				</form>\
				<hr>\
				<form method=\"GET\" action=\"/\">\
					<p><input type=\"submit\" name=\"SENSORS\" value=\"前の画面に戻る\">(設定しない)</p>\
				</form>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title,
			html_title,
				html_checked[BOARD_TYPE==0], html_checked[BOARD_TYPE==1], html_checked[BOARD_TYPE==2],
				html_checked[!TEMP_EN], html_checked[TEMP_EN], TEMP_ADJ, 
				html_checked[!HALL_EN], html_checked[HALL_EN], 
				html_checked[ADC_EN==0], html_checked[ADC_EN==32], html_checked[ADC_EN==33], html_checked[ADC_EN==34], html_checked[ADC_EN==35],
				html_checked[BTN_EN==0], html_checked[BTN_EN==1], html_checked[BTN_EN==2],
				html_checked[PIR_EN==0], html_checked[PIR_EN==1],
				html_checked[IR_IN_EN==0], html_checked[IR_IN_EN==1],html_checked[IR_IN_EN==2], html_checked[IR_IN_EN==3],
				html_checked[AD_LUM_EN==0], html_checked[AD_LUM_EN==1],
				html_checked[AD_TEMP_EN==0], html_checked[AD_TEMP_EN==1], html_checked[AD_TEMP_EN==2],
				html_checked[I2C_HUM_EN==0], html_checked[I2C_HUM_EN==1], html_checked[I2C_HUM_EN==2],
				html_checked[I2C_HUM_EN==3], html_checked[I2C_HUM_EN==4], html_checked[I2C_HUM_EN==5],
				html_checked[I2C_ENV_EN==0], html_checked[I2C_ENV_EN==1], html_checked[I2C_ENV_EN==2],
				html_checked[I2C_ACCEM_EN==0], html_checked[I2C_ACCEM_EN==1],
				html_checked[TIMER_EN==0], html_checked[TIMER_EN==1]
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_display(){
	char s[HTML_INDEX_LEN_MAX];
	char res_s[HTML_RES_LEN_MAX]="";
	
	/////////////// ----------------------
	Serial.println("HTML display ---------");
	
	html_dataAttrSet(res_s);
	int led = digitalRead(PIN_LED);
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s 表示出力設定</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>%s 表示出力設定</h1>\
					<p>%s</p>\
				<form method=\"GET\" action=\"/display\">\
				<h3>LED</h3>\
					<p><input type=\"radio\" name=\"LED\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"LED\" value=\"1\" %s>ON<br>\
					ピン=<input type=\"radio\" name=\"PIN_LED\" value=\"2\" %s>IO2\
					<input type=\"radio\" name=\"PIN_LED\" value=\"4\" %s>IO4\
					<input type=\"radio\" name=\"PIN_LED\" value=\"23\" %s>IO23\
					</p>\
				<h3>LED制御</h3>\
					<p>ON :<a href=\"http://%s/?LED=1\">http://%s/?LED=1</a></p>\
					<p>OFF:<a href=\"http://%s/?LED=0\">http://%s/?LED=0</a></p>\
				<h3>I2C液晶</h3>\
					<p><input type=\"radio\" name=\"LCD_EN\" value=\"0\" %s>OFF\
					<input type=\"radio\" name=\"LCD_EN\" value=\"1\" %s>8x2\
					<input type=\"radio\" name=\"LCD_EN\" value=\"2\" %s>16x2\
					</p>\
				<h3>I2C液晶制御</h3>\
					<p>表示:<input type=\"text\" name=\"DISPLAY\" value=\"LCDﾋｮｳｼﾞbyWataru\" size=\"16\"></p>\
					<p>Hello:<a href=\"http://%s/?DISPLAY=Hello\">http://%s/?DISPLAY=Hello</a></p>\
				<h3>出力設定の実行</h3>\
					<p><input type=\"submit\" value=\"設定\"></p>\
				</form>\
				<hr>\
				<form method=\"GET\" action=\"/\">\
					<input type=\"submit\" name=\"SENSORS\" value=\"前の画面に戻る\">\
				</form>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title,
			html_title, res_s,
				html_checked[led==0], html_checked[led==1], html_checked[PIN_LED==2], html_checked[PIN_LED==4], html_checked[PIN_LED==23],
				html_ip_ui_s, html_ip_ui_s, html_ip_ui_s, html_ip_ui_s,
				html_checked[LCD_EN==0], html_checked[LCD_EN==1], html_checked[LCD_EN==2],
				html_ip_ui_s, html_ip_ui_s
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_sendto(){
	char s[HTML_INDEX_LEN_MAX];
	
	/////////////// ----------------------
	Serial.println("HTML sendto ----------");
	
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s データ送信設定</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
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
					<p>送信単位　\
					<input type=\"radio\" name=\"UDP_MODE\" value=\"1\" %s>センサ毎\
					<input type=\"radio\" name=\"UDP_MODE\" value=\"2\" %s>全値一括\
					<input type=\"radio\" name=\"UDP_MODE\" value=\"3\" %s>両方\
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
					<p>[Wi-Fi 設定]の[スリープ間隔]の設定のほうが優先します</p>\
					<p>Ambientへの送信間隔は30秒以上を推奨します(1日3000サンプルまで)</p>\
					<h3>送信設定の実行</h3>\
					<input type=\"submit\" name=\"SENSORS\" value=\"設定\">(送信の開始)\
				</form>\
				<hr>\
				<form method=\"GET\" action=\"/\">\
					<input type=\"submit\" name=\"SENSORS\" value=\"前の画面に戻る\">(設定しない)\
				</form>\
				<hr>\
				<p>by bokunimo.net</p>\
			</body>\
		</html>", html_title,
			html_title,
			html_checked[UDP_PORT==0], html_checked[UDP_PORT==1024], html_checked[UDP_PORT==3054], html_checked[UDP_PORT==49152],
			html_checked[DEVICE_NUM=='1'], html_checked[DEVICE_NUM=='2'], html_checked[DEVICE_NUM=='3'], html_checked[DEVICE_NUM=='4'], html_checked[DEVICE_NUM=='5'],
			html_checked[UDP_MODE==1], html_checked[UDP_MODE==2], html_checked[UDP_MODE==3],
			AmbientChannelId, AmbientWriteKey,
			html_checked[SEND_INT_SEC==0], html_checked[SEND_INT_SEC==5], html_checked[SEND_INT_SEC==15], html_checked[SEND_INT_SEC==30], html_checked[SEND_INT_SEC==60]
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_pinout(){
	char s[HTML_INDEX_LEN_MAX];
	char buf_s[128];
	int i;
		
	/////////////// ----------------------
	Serial.println("HTML pinout ----------");
	
	snprintf(s, HTML_INDEX_LEN_MAX,
		"<html>\
			<head>\
				<title>%s ピン配列表</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>%s ピン配列表</h1>\
				<p>ボード名：%s</p>\
				<table border=1><tr><th>番号</th><th>ピン名</th><th>接続先</th></tr>\
		", html_title, html_title, sensors_boardName(BOARD_TYPE)
	);
	int low = sensors_pinout_pins_low();
	int high = sensors_pinout_pins();
	for(i=0;i >= 0; i += 2 * (i<low) - 1){	// i: 0,1,2,....low-1, high-1,high-2,....low
		Serial.print(" pin " + String(i+1) + " (" + sensors_pinout_S(i) + ") : ");
		String S = "-";
		if( sensors_pin_assigned_S(i).length() == 0 ) S = "Null";
		else if( !(sensors_pin_assigned_S(i).equals(sensors_pinout_S(i))) ) S = sensors_pin_assigned_S(i) + " へ接続";
		Serial.println(S);
		
		String("<tr><td>" + String(i+1)
			+ "</td><td>" + sensors_pinout_S(i)
			+ "</td><td>" + S
			+ "</td></tr>"
		).toCharArray(buf_s, 128);
		strncat(s,buf_s, HTML_INDEX_LEN_MAX - strlen(s) - 1);
		if( i == low - 1){
			i = high;
			strncat(s,"<tr><th>番号</th><th>ピン名</th><th>接続先</th></tr>", HTML_INDEX_LEN_MAX - strlen(s) - 1);
			Serial.println();
		}
		if( i == low) i = -2;
	}
	strncat(s,
		"		</table>\
				<hr>\
				<form method=\"GET\" action=\"/\">\
					<input type=\"submit\" name=\"SENSORS\" value=\"前の画面に戻る\">\
				</form>\
			</body>\
		</html>", HTML_INDEX_LEN_MAX - strlen(s) - 1
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
}

void html_reboot(){
	char s[HTML_INDEX_LEN_MAX];
	
	/////////////// ----------------------
	Serial.println("HTML reboot ----------");
//	/* SPIFFS //////////////////////////
	if(server.hasArg("SAVE")){
		Serial.println("SAVE to SPIFFS");
				
		if(SPIFFS.begin()){	// ファイルシステムSPIFFSの開始
			File file = SPIFFS.open(FILENAME,"w");       // 保存のためにファイルを開く
			if( file ){
				int size = 1 + 16 + 16 + 17 + 65 + 1 + 1;
				char d[(1 + 16 + 16 + 17 + 65 + 1) + 1 + 1];
				int end = 0;
			//	memset(d,0,size + 1);
				d[end] = '0' + BOARD_TYPE;
				end++;
				strncpy(d+end,SSID_AP,16); end += 16;
				strncpy(d+end,PASS_AP,16); end += 16;
				strncpy(d+end,SSID_STA,17); end += 17;
				strncpy(d+end,PASS_STA,65); end += 65;
				d[end] = '0' + WIFI_AP_MODE;
				end++;
				d[end] = '0' + MDNS_EN;
				end++;
				// int sizeと char dでデータサイズを設定する
				file.write((byte *)d,size);
				file.close();
			} else Serial.println("SAVE ERROR");
			SPIFFS.end();
		} else Serial.println("SPIFSS ERROR");
	}
//	*/
	
	uint32_t ip;
	switch(WIFI_AP_MODE){
		case 1:
			ip = ip_num_ap;
			break;
		case 2:
			ip = ip_num_sta;
			break;
		case 3:
			ip = ip_num_ap;
			break;
	}
	sprintf(html_ip_num_s,"%d.%d.%d.%d",
		ip & 255,
		ip>>8 & 255,
		ip>>16 & 255,
		ip>>24
	);
	if( MDNS_EN ){
		strcpy(html_ip_ui_s,html_ip_mdns_s);
	}else{
		strcpy(html_ip_ui_s,html_ip_num_s);
	}
	
	snprintf(s, HTML_MISC_LEN_MAX,
		"<html>\
			<head>\
				<title>Wi-Fi 再起動中</title>\
				<meta http-equiv=\"refresh\" content=\"12;URL=http://%s/\">\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>Wi-Fi 再起動中</h1>\
				<p>しばらくおまちください(約15秒)</p>\
				<p>STAモードに切り替えたときは,LAN側からアクセスしてください</p>\
				<p>接続できないときはスマートフォンのWi-Fi接続先を確認してください</p>\
				<p>IP：<br><a href=\"http://%s/\">http://%s/</a></p>\
				<p>mDNS：<br><a href=\"http://%s/\">http://%s/</a></p>\
			</body>\
		</html>", html_ip_ui_s, html_ip_num_s, html_ip_num_s, html_ip_mdns_s, html_ip_mdns_s
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
	delay(110);
	server.close();
	TimerWakeUp_setSleepTime(2);
	TimerWakeUp_sleep();
}

void html_gpio_init(){
	Serial.println("HTML gpio_init -------");
	server.send(200, "text/html",
		"<html>\
			<head>\
				<title>GPIO 再起動中</title>\
				<meta http-equiv=\"refresh\" content=\"3;/?SENSORS=GET\">\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>GPIO 再起動中</h1>\
				<p>おまちください(約5秒)</p>\
			</body>\
		</html>");
	sensors_init();
	Serial.print("done html");
}

void html_format(){
	Serial.println("HTML format ----------");
	server.send(200, "text/html",
		"<html>\
			<head>\
				<title>SPIFFS フォーマット中</title>\
				<meta http-equiv=\"refresh\" content=\"3;/?SENSORS=GET\">\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>SPIFFS フォーマット中</h1>\
				<p>おまちください(約5秒)</p>\
			</body>\
		</html>");
	Serial.println("Formating SPIFFS.");
	SPIFFS.format();
	Serial.print("done html");
}

void html_sleep(){
	char s[HTML_INDEX_LEN_MAX];
	
	/////////////// ----------------------
	Serial.println("HTML sleep -----------");
	
	snprintf(s, HTML_MISC_LEN_MAX,
		"<html>\
			<head>\
				<title>Wi-Fi 電源OFF</title>\
				<meta http-equiv=\"Content-type\" content=\"text/html; charset=UTF-8\">\
				<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\
			</head>\
			<body>\
				<h1>Wi-Fi ディープ・スリープへ移行中です</h1>\
				<p>IO %d ピンをLowレベルに設定(BOOTボタン押下)すると復帰します</p>\
				<p>スリープ間隔を設定していた場合は,設定時間後に自動復帰します</p>\
				<p>スマホと本機とのWi-Fiが切れるので,再度,Wi-Fi接続が必要です</p>\
				<p>本機に設定した内容は保持されます(電源OFFやENボタンで消えます)</p>\
				<p>復帰後のアクセス先＝<a href=\"http://%s/\">http://%s/</a></p>\
			</body>\
		</html>", PIN_SW, html_ip_ui_s, html_ip_ui_s
	);
	server.send(200, "text/html", s);
	html_check_overrun(strlen(s));
	delay(110);
	server.close();
	sleep();
}

/*
void html_test(){
	char s[HTML_INDEX_LEN_MAX];
	char res_s[HTML_S_LEN_MAX];
	const char *test16 = "this is test, 16";	// 16+1 bytes
	const char *test32 = "I say someting, THIS IS TEST, 32";	// 32+1 bytes
	
	/////////////// ----------------------
	Serial.println("html_error");
	for(int i=0; i<5;i++){
		html_error(test16,test16,test16);
		Serial.println("len=" + String(strlen(html_error_s)) + ": max=" + String(HTML_ERROR_LEN_MAX));
	}
	
	Serial.println("_html_cat_res_s");
	for(int i=0; i<9;i++){
		_html_cat_res_s(res_s,test32);
		Serial.println("len=" + String(strlen(res_s)) + ": max=" + String(HTML_RES_LEN_MAX) );
	}
	Serial.println(res_s);
	
	Serial.println("snprintf");
	snprintf(res_s, 16,"%s",test32);
	if( 16 - 1 <= strlen(s)) Serial.println("OK");
	else Serial.println("cannot detect");
	
	Serial.println("Test Done");
	server.send(200, "text/plain", "Test Done");
}
*/

/*
void html_text(){
	
	/////////////// ----------------------
	Serial.println("HTML text ------------");
	
	server.send(200, "text/plain", "hello from esp32!");
}
*/

/*
void html_demo(){
	char s[400];
	int sec = millis() / 1000;
	int min = sec / 60;
	int hr = min / 60;
	
	/////////////// ----------------------
	Serial.println("HTML demo ------------");
	
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
*/

void drawGraph() {
	String out = "";
	char temp[100];
	
	/////////////// ----------------------
	Serial.println("HTML drawGraph -------");
	
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
	html_check_overrun(out.length());
}

void html_404(){
	
	/////////////// ----------------------
	Serial.println("HTML 404 -------------");
	
	String message = "File Not Found\n\n";
	message += "URI: ";
	String uri_S = server.uri();
	message += uri_S;
	message += "\nMethod: ";
	message += (server.method() == HTTP_GET) ? "GET" : "POST";
	message += "\nArguments: ";
	message += server.args();
	message += "\n";
	for (uint8_t i = 0; i < server.args(); i++) {
		message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
	}
	server.send(404, "text/plain", message);
	if( uri_S.indexOf("favicon") >= 0 ){
		Serial.println("Requested favicon");
	}else{
		Serial.println(message);
	}
	html_check_overrun(message.length());
}

String html_ipAdrToString(uint32_t ip){
	String S = String(ip & 255) + ".";
	      S += String(ip>>8 & 255) + ".";
	      S += String(ip>>16 & 255) + ".";
	      S += String(ip>>24 & 255);
	return S;
}

void html_init(const char *domainName_local, uint32_t ip, int32_t ip_ap, int32_t ip_sta){
	ip_num_ap = ip_ap;
	ip_num_sta = ip_sta;
	snprintf(html_ip_mdns_s,16,"%s.local",
		domainName_local
	);
	sprintf(html_ip_num_s,"%d.%d.%d.%d",
		ip & 255,
		ip>>8 & 255,
		ip>>16 & 255,
		ip>>24
	);
	if(MDNS_EN && WIFI_AP_MODE == 3){
		strcpy(html_ip_ui_s,html_ip_mdns_s);
	}else{
		strcpy(html_ip_ui_s,html_ip_num_s);
	}
	server.on("/", html_index);
	server.on("/wifi", html_wifi);
	server.on("/sensors", html_sensors);
	server.on("/display", html_display);
	server.on("/pinout", html_pinout);
	server.on("/sendto", html_sendto);
	server.on("/reboot", html_reboot);
	server.on("/gpio_init", html_gpio_init);
	server.on("/sleep", html_sleep);
	server.on("/format", html_format);
//	server.on("/test", html_test);
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
	yield();
}
