#!/usr/bin/env python3
# coding: utf-8
# WebSocketを受信する (サンプル＝ wss://wss.bokunimo.com/ から受信)
# Copyright (c) 2019 Wataru KUNINO

# 実行し、しばらく待つと（2分以内）にkeepaliveなどを受信します

################################################################################
# 下記のライブラリが必要です
# sudo pip3 install websocket-client
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

url = 'wss://wss.bokunimo.com/'
argc = len(sys.argv)                                    # 引数の数をargcへ代入
print('WebSocket Logger (usage:',sys.argv[0],'URL)')    # タイトル表示

if argc >= 2:                                           # 入力パラメータ数の確認
    url = sys.argv[1]                                   # トークンを設定

print('Listening,',url)                                 # URL表示
try:
    sock = websocket.create_connection(url)             # ソケットを作成
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了
while sock:                                             # 作成に成功したとき
    payload = sock.recv()                               # WebSocketを取得
    date=datetime.datetime.today()                      # 日付を取得
    print(date.strftime('%Y/%m/%d %H:%M'), end='')      # 日付を出力
    print(', '+payload)                                 # 受信データを出力
sock.close()                                            # ソケットの切断
