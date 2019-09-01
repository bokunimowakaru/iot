# coding: utf-8
# IoT連携の基本 HTTP GET μsocket for MicroPython (μsocket使用)
# Copyright (c) 2019 Wataru KUNINO

# ご注意：ESP32マイコンのWi-FiをONにします。
# 　　　　使い方を誤ると、電波法に違反する場合があります。
# 　　　　作成者は一切の責任を負いません。

import network                              # ネットワーク通信ライブラリ
import usocket                              # ソケット通信ライブラリ
import ujson                                # JSON変換ライブラリを組み込む
from sys import exit                        # ライブラリsysからexitを組み込む
from machine import Pin                     # ライブラリmachineのPinを組み込む
from time import sleep                      # ライブラリtimeからsleepを組み込む

wifi_ssid = '<AP_name>'                     # Wi-FiアクセスポイントのSSIDを記入
wifi_pass = '<password>'                    # パスワードを記入

host_s = 'bokunimo.net'                     # アクセス先のホスト名
path_s = '/iot/cq/test.json'                # アクセスするファイルパス

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

try:                                        # 例外処理の監視を開始
    addr = usocket.getaddrinfo(host_s, 80)[0][-1]
    sock = usocket.socket()
    sock.connect(addr)
    req = 'GET ' + path_s + ' HTTP/1.0\r\n'
    req += 'Host: ' + host_s + '\r\n\r\n'
    sock.send(bytes(req,'UTF-8'))
except Exception as e:                      # 例外処理発生時
    print(e)                                # エラー内容を表示
    sock.close()
    sta_if.disconnect()                     # Wi-Fiの切断
    sta_if.active(False)                    # Wi-Fiの停止
    exit()

body = '<head>'
while True:
    res = str(sock.readline(), 'UTF-8')
    print(res.strip())
    if len(res) <= 0:
        break
    if res == '\n' or res == '\r\n':
        body = '<body>'
        break
if body != '<body>':
    print('no body data')
    sock.close()
    sta_if.disconnect()                     # Wi-Fiの切断
    sta_if.active(False)                    # Wi-Fiの停止
    exit()

body = ''
while True:
    res = str(sock.readline(), 'UTF-8').strip()
    if len(res) <= 0:
        break
    body += res

print(body)

res_dict = ujson.loads(body)      # 受信データを変数res_dictへ代入
print('--------------------------------------') # -----------------------------
print('title :', res_dict.get('title'))         # 項目'title'の内容を取得・表示
print('descr :', res_dict.get('descr'))         # 項目'descr'の内容を取得・表示
print('state :', res_dict.get('state'))         # 項目'state'の内容を取得・表示
print('url   :', res_dict.get('url'))           # 項目'url'内容を取得・表示
print('date  :', res_dict.get('date'))          # 項目'date'内容を取得・表示

sock.close()                                # ソケットの終了
sta_if.disconnect()                         # Wi-Fiの切断
sta_if.active(False)                        # Wi-Fiの停止
led.value(0)                                # LEDを消灯
