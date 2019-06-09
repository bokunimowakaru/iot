#!/usr/bin/env python3
# coding: utf-8
# UDPを受信する
# Copyright (c) 2018-2019 Wataru KUNINO

import socket
import datetime

print('Listening UDP port', 1024, '...')                # ポート番号1024表示
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了
while sock:                                             # 永遠に繰り返す
    udp = sock.recv(64).decode().strip()                # UDPパケットを取得
    if udp.isprintable():                               # 全文字が表示可能
        date=datetime.datetime.today()                  # 日付を取得
        print(date.strftime('%Y/%m/%d %H:%M'), end='')  # 日付を出力
        print(', ' + udp)                               # 受信データを出力
