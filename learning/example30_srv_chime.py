#!/usr/bin/env python3
# coding: utf-8

# Example 29 IoTボタンでチャイム音・玄関呼び鈴システム
# IoTボタンが送信するUDPを受信し、IoTチャイムへ鳴音指示を送信する

# 接続図
#           [IoTボタン] ------> [本機] ------> [IoTチャイム]
#           ボタン操作                           チャイム音

# 機器構成
#   本機        IoTボタンが押されたときにIoTチャイムへ鳴音指示
#   IoTボタン   example14_iot_btn.py
#   IoTチャイム example18_iot_chime_n.py

ip_chime = '127.0.0.1'                          # IoTチャイムのIPアドレス

import socket                                   # IP通信用モジュールの組み込み
import urllib.request                           # HTTP通信ライブラリを組み込む

def chime():                                            # チャイム
    url_s = 'http://' + ip_chime                        # アクセス先をurl_sへ
    try:
        urllib.request.urlopen(url_s)                   # IoTチャイムへ鳴音指示
    except urllib.error.URLError:                       # 例外処理発生時
        print('URLError :',url_s)                       # エラー表示
        # ポート8080へのアクセス用 (下記の5行)
        url_s = 'http://' + ip_chime + ':8080'          # ポートを8080に変更
        try:
            urllib.request.urlopen(url_s)               # 再アクセス
        except urllib.error.URLError:                   # 例外処理発生時
            print('URLError :',url_s)                   # エラー表示

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while sock:                                             # 永遠に繰り返す
    udp, udp_from = sock.recvfrom(64)                   # UDPパケットを取得
    udp = udp.decode().strip()                          # データを文字列へ変換
    if udp == 'Ping':                                   # 「Ping」に一致する時
        print('device = Ping',udp_from[0])              # 取得値を表示
        chime()                                         # chimeの起動

'''
実行例

pi@raspberrypi:~ $ cd ~/iot/learning/
pi@raspberrypi:~/iot/learning $ ./example30_srv_chime.py
Listening UDP port 1024 ... 
device = Ping 192.168.0.3
device = Ping 192.168.0.3 
--------------------------------------------------------------------------------
pi@raspberrypi:~ $ cd ~/iot/learning/
pi@raspberrypi:~/iot/learning $ ./example14_iot_btn.py
./example14_iot_btn.py
GPIO26 = 0 Ping
GPIO26 = 1 Pong 
GPIO26 = 0 Ping
GPIO26 = 1 Pong
--------------------------------------------------------------------------------
pi@raspberrypi:~ $ cd ~/iot/learning/
pi@raspberrypi:~/iot/learning $ sudo ./example18_iot_chime_nn.py
HTTP port 80
level = 0
127.0.0.1 - - [16/Sep/2019 19:05:14] "GET / HTTP/1.1" 200 9
level = 0
127.0.0.1 - - [16/Sep/2019 19:05:20] "GET / HTTP/1.1" 200 9
'''