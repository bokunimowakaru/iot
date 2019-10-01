#!/usr/bin/env python3
# coding: utf-8

# Example 33 WebSocketを受信する
# Copyright (c) 2019 Wataru KUNINO

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

API_ID = '**********'                                   # AWS API Gatewayで取得
REGION = 'us-west-2'                                    # AWSのリージョン
STAGE  = 'Prod'                                         # デプロイ時のステージ名
KEY    = 'message'                                      # API ルート選択

import websocket                                        # WebSocketライブラリ
import datetime                                         # 日時ライブラリ
import urllib.request                                   # HTTP通信ライブラリ
import json                                             # JSON変換ライブラリ

if API_ID == '**********':
    res = urllib.request.urlopen('https://bokunimo.net/iot/cq/test_ws_aws.json')
    res_dict = json.loads(res.read().decode().strip())
    API_ID = res_dict.get('api_id')
    REGION = res_dict.get('region')
    STAGE  = res_dict.get('stage')
    KEY    = res_dict.get('key')
    res.close()

print('WebSocket Logger')                               # タイトル表示
url = 'wss://' + API_ID + '.execute-api.' + REGION + '.amazonaws.com/' + STAGE
print('Listening,',url)                                 # URL表示
try:
    sock = websocket.create_connection(url)             # ソケットを作成
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了
while sock:                                             # 作成に成功したとき
    payload = sock.recv().strip()                       # WebSocketを取得
    date=datetime.datetime.today()                      # 日付を取得
    print(date.strftime('%Y/%m/%d %H:%M'), end='')      # 日付を出力
    try:
        res_dict = json.loads(payload)
        print(',', res_dict.get('message'))             # 受信データを出力
    except Exception:
        print(',', payload)                             # 受信データを出力
sock.close()                                            # ソケットの切断
