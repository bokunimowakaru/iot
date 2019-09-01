# coding: utf-8
# IoT連携 Ambientへ送信 HTTP POST μrequests for MicroPython (μrequests使用)
# Copyright (c) 2019 Wataru KUNINO

# ご注意：ESP32マイコンのWi-FiをONにします。
# 　　　　使い方を誤ると、電波法に違反する場合があります。
# 　　　　作成者は一切の責任を負いません。

wifi_ssid = '<AP_name>'                     # Wi-FiアクセスポイントのSSIDを記入
wifi_pass = '<password>'                    # パスワードを記入
ambient_chid='0000'                         # Ambientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef'             # ここにはライトキーを入力
amdient_tag='d1'                            # データ番号d1～d8のいずれかを入力
temp_offset = 30.0                          # CPU温度上昇値(要調整)

import network                              # ネットワーク通信ライブラリ
import urequests                            # HTTP通信ライブラリ
from sys import exit                        # ライブラリsysからexitを組み込む
from machine import Pin, deepsleep          # GPIO用Pinとディープスリープを組込
from time import sleep                      # ライブラリtimeからsleepを組み込む
from esp32 import raw_temperature

url = 'http://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head = {'Content-Type':'application/json'}  # ヘッダを変数head_dictへ
body = {'writeKey':ambient_wkey, amdient_tag:0.0}  # 内容を変数bodyへ

led = Pin(2, Pin.OUT)                       # GPIO出力用インスタンスledを生成
led.value(1)                                # LEDを点灯
sta_if = network.WLAN(network.STA_IF)       # Wi-Fi接続用インスタンスの生成
sta_if.active(True)                         # Wi-Fiの起動
sta_if.scan()                               # Scan for available access points
sta_if.connect(wifi_ssid, wifi_pass)        # Connect to an AP

while not sta_if.isconnected():             # Check for successful connection
    print('.', end='')
    led.value(not led.value())
    sleep(0.5)                              # 0.5秒間の待ち時間処理(低速点滅)

# 温度を取得する
temp = (raw_temperature() - 32) * 5 / 9     # 温度を取得
temp = round(temp - temp_offset, 1)         # 温度補正と小数第二位以下の丸め処理
print('Temperature =',temp)                 # 温度を表示する
body[amdient_tag] = temp                    # 辞書型変数body内に埋め込む

# Ambientへ送信する
try:                                        # 例外処理の監視を開始
    res = urequests.post(url, json=body, headers=head)  # HTTPリクエストを送信
    print('HTTP Status Code =', res.status_code)
except Exception as e:                      # 例外処理発生時
    print(e)                                # エラー内容を表示
    sta_if.disconnect()                     # Wi-Fiの切断
    sta_if.active(False)                    # Wi-Fiの停止
    exit()

sta_if.disconnect()                         # Wi-Fiの切断
sta_if.active(False)                        # Wi-Fiの停止
led.value(0)                                # LEDを消灯
# deepsleep(30000)                          # 30秒間スリープ
