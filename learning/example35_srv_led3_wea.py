#!/usr/bin/env python3
# coding: utf-8
# Example 35 インターネット照る照る坊主 【IoT カラーLEDを制御】

# 接続図
#           [天気予報] (インターネット)
#             ↓
#           [本機] ------> [IoTカラーLED] or [IoTフルカラーLED]
#
# 機器構成
#   本機                天気情報を色番号に変換してIoTカラーLEDを点灯制御
#   IoTカラーLED        example14_iot_btn.py    初期設定内の colors_full=False
#   IoTフルカラーLED    example19_iot_ledpwm.py 初期設定内の colors_full=True
#
# ESP8266用：
# https://github.com/bokunimowakaru/esp/blob/master/2_example/example16f_led/example16f_led.ino
#
# ESP32用：
# https://github.com/bokunimowakaru/esp/blob/master/2_example/example48f_led/example48f_led.ino
#
# 天気情報・参考文献：
# http://weather.livedoor.com/weather_hacks/webservice



# 初期設定
ip_leds = ['127.0.0.1']                             # IoTカラーLEDのIPアドレス
colors = ['消灯','赤色','緑色','黄色','青色','赤紫色','藍緑色','白色']

# フルカラーLEDを使用する場合はcolors_full=Trueを設定
colors_full = True                                  # フルカラー有効化フラグ

city_id = 270000                                    # 大阪の city ID=270000
                                                    # 東京=130010 京都=260010
                                                    # 横浜=140010 千葉=120010
                                                    # 名古屋=230010 福岡=400010
url_wea_s = 'http://weather.livedoor.com/forecast/webservice/json/v1?city='
url_wea_s += str(city_id)
interval = 10 * 60                                  # 動作間隔10分（単位＝秒）

# ライブラリ
import urllib.request                               # HTTP通信ライブラリを組込む
import json                                         # JSON変換ライブラリを組込む
from time import sleep                              # スリープ実行モジュール

def getWeather():                                   # 天気予報情報取得関数を定義
    try:                                            # 例外処理の監視を開始
        res = urllib.request.urlopen(url_wea_s)     # HTTPアクセスを実行
        res_s = res.read().decode()                 # 受信テキストを変数res_sへ
        res.close()                                 # HTTPアクセスの終了
        res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
    except Exception as e:
        print(e)                                    # エラー内容を表示
        return None                                 # Noneを応答
    return res_dict['forecasts'][0]['telop']        # 天候の予報情報を応答

def led3(ip,color):                                 # IoTカラーLED
    if color is None or color < 0 or color > 7:     # 範囲外の値の時に
        return                                      # 何もせずに戻る
    url_led_s = 'http://' + ip                      # アクセス先
    if colors_full:                                 # フルカラーの設定
        colors_3 = ['R','G','B']                    # 3原色名R,G,Bを代入
        colors_rgb = ['000','933','393','770','339','717','276','666']  # カラー
        s = '/?'                                    # 文字列変数sの初期化
        for i in range(len(colors_3)):              # 文字変数cにR、G、Bを代入
            s += colors_3[i] + "="                  # 変数sにR=、G=、B=を追加
            s += colors_rgb[color][i]               # 各色の輝度(0～9)を追加
            if i < len(colors_3) - 1:               # forに次の3原色がある場合
                s += '&'                            # 結合を示す「&」を追加
    else:
        s = '/?COLOR=' + str(color)                 # 色番号(0～7)の設定
    try:
        urllib.request.urlopen(url_led_s + s)       # IoTカラーLEDへ色情報を送信
    except urllib.error.URLError:                   # 例外処理発生時
        print('URLError :',url_led_s)               # エラー表示
        # ポート8080へのアクセス用 (下記の5行)
        url_led_s = 'http://' + ip + ':8080'        # ポートを8080に変更
        try:
            urllib.request.urlopen(url_led_s + s)   # 再アクセス
        except urllib.error.URLError:               # 例外処理発生時
            print('URLError :',url_led_s)           # エラー表示

while True:
    telop = getWeather()                            # 天気情報を取得
    print('telop =', telop)                         # telopの内容を表示
    if telop is not None:
        color = colors.index('消灯')                # 初期カラー番号を白色=7に
        if telop.find('晴') >= 0:                   # 晴れが含まれているとき
            color |= colors.index('赤色')           # 赤色を混合
        if telop.find('曇') >= 0:                   # 曇りが含まれているとき
            color |= colors.index('緑色')           # 緑色を混合
        if telop.find('雨') >= 0 or telop.find('雪') >= 0:  # 雨or雪のとき
            color |= colors.index('青色')           # 青色を混合
        color %= len(colors)                        # colorは0～7
        print('Color =',color,colors[color])        # 色番号と色名を表示
        for ip in ip_leds:                          # 各機器のIPアドレスをipへ
            led3(ip,color)                          # 各IoTカラーLEDに色を送信
    sleep(interval)                                 # 動作間隔の待ち時間処理

'''
実行例
--------------------------------------------------------------------------------
pi@raspberrypi:~/iot/learning $ ./example35_srv_led3_wea.py
telop = 晴れのち曇り
Color = 3 黄色
telop = 曇り
Color = 2 緑色
--------------------------------------------------------------------------------
pi@raspberrypi:~/iot/learning $ sudo ./example19_iot_ledpwm.py
127.0.0.1 - - [11/Oct/2019 17:54:24] "GET /?R=3&G=9&B=3 HTTP/1.1" 200 17
Color = [7, 7, 0]
GPIO17 = 35
GPIO27 = 35
GPIO22 = 0
127.0.0.1 - - [11/Oct/2019 18:04:24] "GET /?R=3&G=9&B=3 HTTP/1.1" 200 17
Color = [3, 9, 3]
GPIO17 = 4
GPIO27 = 100
GPIO22 = 4
--------------------------------------------------------------------------------
'''
