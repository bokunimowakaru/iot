#!/usr/bin/env python3
# coding: utf-8

################################################################################
## ご注意：
## 本プログラムは Raspberry Pi 5 に対応するために、GPIO用ライブラリにGPIO Zeroを
## 使用します。
## Raspberry Pi 4 以前でも動作します。
## 書籍「Pythonで作るIoTシステム プログラム・サンプル集」のリストからの変更点は
## 変更前を各行の先頭の#で示し、変更後を各行のコメントの##で示します。
## 書籍と同じプログラムは、プログラム名に「_rpi」を付与して収録してあります。
################################################################################

# Example 34 インターネット照る照る坊主

# 参考文献 天気予報 API（livedoor 天気互換サービス）：
# https://weather.tsukumijima.net/
#
# 【重要なご注意】
# livedoor 天気 のサービス終了に伴い、上記の互換サービスを利用します。
# 同サービスや本ソフトウェアの利用に関して、筆者(国野 亘)は、責任を負いません。
# 同サービスは、気象庁による気象予報をlivedoor天気の互換形式に変換して配信します。
# (2023年1月28日現在、気象予報そのものは行っていない)
# 気象業務法や、下記の予報業務許可に関する情報、上記参考文献の注意事項を
# 良く読んでから利用ください。
# 気象業務法   https://www.jma.go.jp/jma/kishou/info/ml-17.html
# 予報業務許可 https://www.jma.go.jp/jma/kishou/minkan/q_a_m.html

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
url_wea_s = 'https://weather.tsukumijima.net/api/forecast?city='
url_wea_s += str(city_id)

# ライブラリの組み込み
# from RPi import GPIO                          # GPIOライブラリを組み込む
from gpiozero import LED                        ## GPIO ZeroのI/Oモジュール取得
from signal import pause                        # シグナル待ち受けの取得
import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

# GPIO初期化
# GPIO.setmode(GPIO.BCM)                        # ポート番号の指定方法の設定
# GPIO.setwarnings(False)                       # ポート警告表示を無効に
leds = list()                                   ## LEDインスタンス用
for port in ports:                              # 各ポート番号を変数portへ代入
    # GPIO.setup(port, GPIO.OUT)                # ポート番号portのGPIOを出力に
    leds.append(LED(port))                      ## GPIO ZeroのLEDを実体化

# 天気情報の取得
try:                                            # 例外処理の監視を開始
    req = urllib.request.Request(url_wea_s,headers={"User-Agent": "led3_wea"})
    res = urllib.request.urlopen(req)           # HTTPアクセスを実行
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

# 取得した情報から天候情報を抽出
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
    # GPIO.output(port, b)                      # ポート番号portのGPIOを出力に
    leds[i].value = b                           ## ↑
print('[Ctrl]+[C]で終了します')
pause()                                         ## 待ち受け待機する(永久ループ)

'''
pi@raspberrypi:~/iot/learning $ ./example34_weather_led3.py
city = 大阪府 大阪
telop = 曇り
Color = 2 緑色
GPIO17 = 0
GPIO27 = 1
GPIO22 = 0
'''
