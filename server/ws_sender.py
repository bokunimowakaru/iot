#!/usr/bin/env python3
# coding: utf-8
# WebSocketを送信する
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

url = 'wss://api.sakura.io/ws/v1/'
talken = '00000000-0000-0000-0000-000000000000'         # sakura.ioのTalkenを記入
module_id = 'u00000000000'
module_ch = 1

argc = len(sys.argv)                                    # 引数の数をargcへ代入
print('WebSocket Sender (usage:',sys.argv[0],'talken)') # タイトル表示

if argc == 2:                                           # 入力パラメータ数の確認
    talken = sys.argv[1]                                # トークンを設定

url += talken                                           # トークンを連結
sock = websocket.create_connection(url)                 # ソケットを作成
print('stdin\n> ',end='')
while sock:                                             # 作成に成功したとき
    for line in sys.stdin:                              # 標準入力から変数lineへ
        line = line.strip('\r\n')
        if line.isdecimal():
            val=int(line)                               # 数値を取得しvalへ代入
            print('val =',val)
            payload = '{"channels":[{"channel":'\
                + str(module_ch)\
                + ',"type":"I","value":'\
                + str(val)\
                + '}]}'
        else:
            s=''
            for c in line:
                if ord(c) >= 16:
                    s += format(ord(c),'x')
            print('code =',s)
            payload = '{"channels":[{"channel":'\
                + str(module_ch)\
                + ',"type":"b","value":"'\
                + s\
                + '"}]}'
            print(payload)
            exit

        json_s = '{"type":"channels","module":"'\
            + module_id\
            + '",'\
            + '"payload":'\
            + payload\
            + '}'
        sock.send(json_s)                              # WebSocket送信
        print(sock.recv())                             # WebSocketを取得
        print('\n> ',end='')
sock.close()                                           # ソケットの切断
