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
    udp = sock.recv(64).decode().strip()                # UDPパケットを取得
    if udp.isprintable() and len(udp) <= 4:             # 4文字以下で表示可能
        if udp == 'Ping':                               # 「Ping」に一致する時
            b = 1                                       # 変数bに1を代入
        else:                                           # その他のとき
            b = 0                                       # 変数bに0を代入
        print(udp, ', b =', b)                          # 取得値を表示
