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
url_s = 'http://' + ip_chime                    # アクセス先を変数url_sへ代入

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
    if udp.isprintable() and len(udp) <= 4:             # 4文字以下で表示可能
        if udp == 'Ping':                               # 「Ping」に一致する時
            b = 1                                       # 変数bに1を代入
            try:
                urllib.request.urlopen(url_s)           # IoTチャイムへ鳴音指示
            except urllib.error.URLError:               # 例外処理発生時
                print('URLError :',url_s)               # エラー表示
                # ポート8080へのアクセス用 (下記の5行)
                url_s = 'http://' + ip_chime + ':8080'  # ポートを8080に変更
                try:
                   urllib.request.urlopen(url_s)        # 再アクセス
                except urllib.error.URLError:           # 例外処理発生時
                   url_s = 'http://' + ip_chime         # ポートを戻す
        else:                                           # その他のとき
            b = 0                                       # 変数bに0を代入
        print(udp_from[0], ',', udp, ', b =', b)        # 取得値を表示
