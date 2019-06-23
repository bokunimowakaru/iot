#!/usr/bin/env python3
# coding: utf-8
# Example 22 IoTボタンを受信する

import socket

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
        else:                                           # その他のとき
            b = 0                                       # 変数bに0を代入
        print(udp_from[0], ',', udp, ', b =', b)        # 取得値を表示
'''
pi@raspberrypi:~/iot/learning $ ./example22_rx_btn.py
Listening UDP port 1024 ...
192.168.0.8 , Ping , b = 1
192.168.0.8 , Pong , b = 0
'''
