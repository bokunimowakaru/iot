#!/usr/bin/env python3
# coding: utf-8

# Example 37 IoTボタンでチャイム音＋写真撮影するカメラ付き玄関呼び鈴システム
# IoTボタンが送信するUDPを受信し、写真撮影とIoTチャイムへ鳴音指示を送信する

# 接続図
#           [IoTボタン] ------> [本機] ------> [IoTチャイム]
#           ボタン操作            ↓             チャイム音
#                               [IoTカメラ]
#                               写真撮影

# 機器構成
#   本機        IoTボタンが押されたときにIoTチャイムへ鳴音指示
#   IoTボタン   example14_iot_btn.py
#   IoTチャイム example18_iot_chime_n.py
#   IoTカメラ   example36_iot_cam.py

ip_cams = ['192.168.0.5']   ## 要設定 ##                # IoTカメラのIPアドレス
ip_chimes = ['127.0.0.1']                               # IoTチャイム,IPアドレス

import socket                                           # IP通信用モジュール
import urllib.request                                   # HTTP通信ライブラリ
import datetime                                         # 日時・時刻用ライブラリ

def chime(ip):                                          # IoTチャイム
    url_s = 'http://' + ip                              # アクセス先をurl_sへ
    try:
        res = urllib.request.urlopen(url_s)             # IoTチャイムへ鳴音指示
    except urllib.error.URLError:                       # 例外処理発生時
        url_s = 'http://' + ip + ':8080'                # ポートを8080に変更
        try:
            urllib.request.urlopen(url_s)               # 再アクセス
        except urllib.error.URLError:                   # 例外処理発生時
            print('URLError :',url_s)                   # エラー表示

def cam(ip):                                            # IoTカメラ
    url_s = 'http://' + ip                              # アクセス先をurl_sへ
    s = '/cam.jpg'
    try:
        res = urllib.request.urlopen(url_s + s)         # IoTカメラで撮影を実行
        if res.headers['content-type'].find('image/jpeg') < 0:
            res = None
    except urllib.error.URLError:                       # 例外処理発生時
        res = None
    if res is None:
        url_s = 'http://' + ip + ':8080'                # ポートを8080に変更
        try:
            res = urllib.request.urlopen(url_s + s)     # 再アクセス
            if res.headers['content-type'].find('image/jpeg') < 0:
                res = None
        except urllib.error.URLError:                   # 例外処理発生時
            res = None
    if res is None:
            print('URLError :',url_s)                   # エラー表示
            return None
    data = res.read()
    date = datetime.datetime.today().strftime('%d%H%M')
    filename = 'cam_' + ip[-1] + '_' + date + '.jpg'
    try:
        fp = open(filename, 'wb')                       # 保存用ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
        return
    fp.write(data)
    fp.close()
    print('filename =',filename)
    return filename

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
        for ip in ip_chimes:                          # 各機器のIPアドレスをipへ
            chime(ip)                          # 各IoTカラーLEDに色を送信
        for ip in ip_cams:                          # 各機器のIPアドレスをipへ
            cam(ip)                          # 各IoTカラーLEDに色を送信

'''
実行例
--------------------------------------------------------------------------------
pi@raspberrypi:~ $ cd ~/iot/learning/
pi@raspberrypi:~/iot/learning $ ./example37_srv_cam.py
Listening UDP port 1024 ... 
device = Ping 192.168.0.3
filename = cam_5_121705.jpg
device = Ping 192.168.0.3 
filename = cam_5_121706.jpg
--------------------------------------------------------------------------------
pi@raspberrypi:~ $ cd ~/iot/learning/
pi@raspberrypi:~/iot/learning $ ./example14_iot_btn.py
./example14_iot_btn.py
GPIO26 = 0 Ping
GPIO26 = 1 Pong 
GPIO26 = 0 Ping
GPIO26 = 1 Pong
--------------------------------------------------------------------------------
IoTチャイム 【example18_iot_chime_n.py】
--------------------------------------------------------------------------------
pi@raspberrypi:~ $ cd ~/iot/learning/
pi@raspberrypi:~/iot/learning $ sudo ./example18_iot_chime_n.py
HTTP port 80
127.0.0.1 - - [12/Oct/2019 17:05:50] "GET / HTTP/1.1" 200 9
127.0.0.1 - - [12/Oct/2019 17:06:05] "GET / HTTP/1.1" 200 9
--------------------------------------------------------------------------------
IoT カメラ【example36_iot_cam.py】
--------------------------------------------------------------------------------
pi@raspberrypi:~ $ cd iot/learning/
pi@raspberrypi:~/iot/learning $ sudo ./example36_iot_cam.py
HTTP port 80
192.168.0.3 - - [12/Oct/2019 17:05:50] "GET /cam.jpg HTTP/1.1" 200 169388
192.168.0.3 - - [12/Oct/2019 17:06:05] "GET /cam.jpg HTTP/1.1" 200 169705
--------------------------------------------------------------------------------
'''
