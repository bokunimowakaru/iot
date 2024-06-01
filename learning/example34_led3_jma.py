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
# 参考文献 同サービスのソースコード
# https://github.com/tsukumijima/weather-api
# https://github.com/tsukumijima/weather-api/blob/master/app/Models/Weather.php
#
#   予報情報の取得：
#   jma_api_forecast = "https://www.jma.go.jp/bosai/forecast/data/forecast/{$prefecture_id}.json";
#
#   概要テキスト(テロップ)の取得：
#   jma_api_overview = "https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{$prefecture_id}.json";
#
# 【重要なご注意】
# 本ソフトウェアの利用に関して、筆者(国野 亘)は、責任を負いません。
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

city_id = 270000                                # 気象庁=130000(東京地方など)
                                                # 大阪管区気象台=270000(大阪府など)
                                                # 京都地方気象台=260000(南部など)
                                                # 横浜地方気象台=140000(東部など)
                                                # 銚子地方気象台=120000(北西部など)
                                                # 名古屋地方気象台=230000(西部など)
                                                # 福岡管区気象台=400000(福岡地方など)

url_s = 'https://www.jma.go.jp/bosai/forecast/data/forecast/'
url_s += str(city_id) + '.json'

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
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
    res_s = res.read().decode()                 # 受信テキストを変数res_sへ
    res.close()                                 # HTTPアクセスの終了
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

# 取得した情報から予報機関(気象庁、気象台)と地域名を抽出して表示する
office = res_dict[0].get('publishingOffice')    # res_dict内のpublishingOffice
timeSeries = res_dict[0].get('timeSeries')      # res_dict内のtimeSeriesを取得
areas = timeSeries[0].get('areas')              # timeSeries内のareasを取得
area = areas[0].get('area').get('name')         # areas内のarea.nameを取得
print('地域 =', office, area)                # officeとareaの内容を表示

# 取得した情報から天気予報を抽出して表示する（予報対象時刻と、予報内容）
weathers = areas[0].get('weathers')             # areas内のweathersを取得
weather = weathers[0]                           # 先頭の天気情報を取得
i = weather.find('　')                          # 3語中1語目の終わり位置を取得
i += weather[i+1:].find('　') + 1               # 3語中2語目の終わり位置を取得
i += weather[i+1:].find('　') + 1               # 3語中3語目の終わり位置を取得
telop = weather[0:i]                            # 3語をtelopに代入
print('予報 =', telop)                          # timeとweatherの内容を表示

# 天候の内容に応じた色を変数colorへ合成
color = colors.index('消灯')                    # 初期カラー番号を白色（7）に
if telop.find('晴') >= 0:                       # 晴れが含まれているとき
    color |= colors.index('赤色')               # 赤色を混合
if telop.find('くもり') >= 0:                   # くもりが含まれているとき
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
pi@raspberrypi:~/iot/learning $ ./example34_led3_jma.py
地域 = 大阪管区気象台 大阪府
予報 = くもり　時々　晴れ
Color = 3 黄色
GPIO17 = 1
GPIO27 = 1
GPIO22 = 0
'''
