#!/usr/bin/env python3
# coding: utf-8
# Example 34 インターネット照る照る坊主

# 参考文献：http://weather.livedoor.com/weather_hacks/webservice

# 初期設定
port_R = 17                                     # 赤色LED用 GPIO ポート番号
port_G = 27                                     # 緑色LED用 GPIO ポート番号
port_B = 22                                     # 青色LED用 GPIO ポート番号
ports = [port_R, port_G, port_B]
colors= ['消灯','赤色','緑色','黄色','青色','赤紫色','藍緑色','白色']

city_id = 270000                                # 大阪の city ID=270000
                                                # 東京=130010 京都=260010
                                                # 横浜=140010 千葉=120010
                                                # 名古屋=230010 福岡=400010
url_wea_s = 'http://weather.livedoor.com/forecast/webservice/json/v1?city='
url_wea_s += str(city_id)

# ライブラリの組み込み
from RPi import GPIO                            # GPIOライブラリを組み込む
import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

# GPIO初期化
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setwarnings(False)                         # ポート警告表示を無効に
for port in ports:                              # 各ポート番号を変数portへ代入
    GPIO.setup(port, GPIO.OUT)                  # ポート番号portのGPIOを出力に

# 天気予報情報の取得
try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(url_wea_s)     # HTTPアクセスを実行
    res_s = res.read().decode()                 # 受信テキストを変数res_sへ
    res.close()                                 # HTTPアクセスの終了
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

# 取得した情報から都道府県名と市町村名を抽出
location = res_dict.get('location')             # res_dict内のlocationを取得
pref = location.get('prefecture')               # location内のprefectureを取得
city = location.get('city')                     # location内のcityを取得
print('city =', pref, city)                     # prefとcityの内容を表示

# 取得した情報から天候の予報情報を抽出
forecasts = res_dict.get('forecasts')           # res_dict内のforecastsを取得
telop = forecasts[0].get('telop')               # forecasts内のtelopを取得
print('telop =', telop)                         # telopの内容を表示

# 天候の内容に応じた色を変数colorへ合成
color = colors.index('消灯')                    # 初期カラー番号を白色（7）に
if telop.find('晴') >= 0:                       # 晴れが含まれているとき
    color |= colors.index('赤色')               # 赤色を混合
if telop.find('曇') >= 0:                       # 曇りが含まれているとき
    color |= colors.index('緑色')               # 緑色を混合
if telop.find('雨') >= 0 or telop.find('雪') >= 0:  # 雨or雪が含まれているとき
    color |= colors.index('青色')               # 青色を混合
color %= len(colors)                            # 色数(8色)に対してcolorは0～7
print('Color =',color,colors[color])            # 色番号と色名を表示

# 変数colorに応じてLEDの色をGPIO出力
for i in range( len(ports) ):                   # 各ポート番号のindexを変数iへ
    port = ports[i]                             # ポート番号をportsから取得
    b = (color >> i) & 1                        # 該当LEDへの出力値を変数bへ
    print('GPIO'+str(port),'=',b)               # ポート番号と変数bの値を表示
    GPIO.output(port, b)                        # ポート番号portのGPIOを出力に

'''
pi@raspberrypi:~/iot/learning $ ./example34_weather_led3.py
city = 大阪府 大阪
telop = 曇り
Color = 2 緑色
GPIO17 = 0
GPIO27 = 1
GPIO22 = 0
'''
