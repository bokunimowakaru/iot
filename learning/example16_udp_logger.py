#!/usr/bin/env python3
# coding: utf-8
# UDPを受信する
# Copyright (c) 2018-2019 Wataru KUNINO

import socket
import datetime

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了
while sock:                                             # 永遠に繰り返す
    udp = sock.recv(64)                                 # UDPパケットを取得
    udp = udp.decode()                                  # 文字列へ変換する
    udp = udp.strip()                                   # 先頭末尾の改行削除
    if udp.isprintable():                               # 全文字が表示可能
        date=datetime.datetime.today()                  # 日付を取得
        print(date.strftime('%Y/%m/%d %H:%M'), end='')  # 日付を出力
        print(', ' + udp, flush=True)                   # 受信データを出力
