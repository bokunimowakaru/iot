#!/usr/bin/env python3
# coding: utf-8
# WebSocketを送信する
# Copyright (c) 2019 Wataru KUNINO

################################################################################
# AWS側のセットアップ方法：
# https://bokunimo.net/blog/raspberry-pi/605/

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

API_ID = '**********'                                   # AWS API Gatewayで取得
REGION = 'us-west-2'                                    # AWSのリージョン
STAGE  = 'Prod'                                         # デプロイ時のステージ名
KEY    = 'message'                                      # API ルート選択

argc = len(sys.argv)                                    # 引数の数をargcへ代入
print('WebSocket Sender (usage: echo "test" |',sys.argv[0],')') # タイトル表示

url = 'wss://' + API_ID + '.execute-api.' + REGION + '.amazonaws.com/' + STAGE
print(url)

try:
    sock = websocket.create_connection(url)             # ソケットを作成
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

print('stdin\n> ',end='')
while sock:                                             # 作成に成功したとき
    for line in sys.stdin:                              # 標準入力から変数lineへ
        line = line.strip('\r\n')
        json_s = '{"' + KEY +'":"sendmessage","data":"' + line + '"}'
        print(json_s)
        sock.send(json_s)                               # WebSocket送信
        print(sock.recv())                              # WebSocketを取得
        print('\n> ',end='')
sock.close()                                            # ソケットの切断
