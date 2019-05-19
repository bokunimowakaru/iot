#!/usr/bin/env python3
# coding: utf-8
# WebSocketを受信する
# Copyright (c) 2019 Wataru KUNINO

################################################################################
# 下記のライブラリが必要です
# pip3 install websocket-client
'''
    Name: websocket-client
    Version: 0.56.0
    Summary: WebSocket client for Python. hybi13 is supported.
    Home-page: https://github.com/websocket-client/websocket-client.git
    Author: liris
    Author-email: liris.pp@gmail.com
    License: BSD
    Location: /home/pi/.local/lib/python3.5/site-packages
    Requires: six
'''

import sys
import websocket
import datetime

url = 'wss://api.sakura.io/ws/v1/'
talken = '00000000-0000-0000-0000-000000000000'         # sakura.ioのTalkenを記入
buf_n= 128                                              # 受信バッファ容量(バイト)
argc = len(sys.argv)                                    # 引数の数をargcへ代入
print('WebSocket Logger (usage:',sys.argv[0],'talken)') # タイトル表示

if argc == 2:                                           # 入力パラメータ数の確認
    talken = sys.argv[1]                                # トークンを設定

url += talken                                           # トークンを連結
print('Listening,',url)                                 # URL表示
sock = websocket.create_connection(url)                 # ソケットを作成
while sock:                                             # 作成に成功したとき
    payload=sock.recv()                                 # WebSocketを取得
    date=datetime.datetime.today()                      # 日付を取得
    print(date.strftime('%Y/%m/%d %H:%M'), end='')      # 日付を出力
    print(', '+payload)                                 # 受信データを出力
sock.close()                                            # ソケットの切断
