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
keys = ['type','sockets','total','data','value','device','url']     # 受信項目名

import websocket                                        # WebSocketライブラリ
import datetime                                         # 日時ライブラリ
import urllib.request                                   # HTTP通信ライブラリ
import json                                             # JSON変換ライブラリ

if API_ID == '**********':                              # 設定値のダウンロード
    res = urllib.request.urlopen('https://bokunimo.net/iot/cq/test_ws_aws.json')
    res_dict = json.loads(res.read().decode().strip())  # 設定値を辞書型変数へ
    API_ID = res_dict.get('api_id')                     # AWS API GatewayのID
    REGION = res_dict.get('region')                     # AWSのリージョン
    STAGE  = res_dict.get('stage')                      # デプロイ時のステージ名
    res.close()                                         # HTTPリクエスト終了

print('WebSocket Logger')                               # タイトル表示
url = 'wss://' + API_ID + '.execute-api.' + REGION + '.amazonaws.com/' + STAGE
print('Listening,',url)                                 # URL表示

try:
    sock = websocket.create_connection(url)             # ソケットを作成
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了
while sock:                                             # 作成に成功したとき
    try:
        payload = sock.recv().strip()                   # WebSocketを取得
    except websocket.WebSocketConnectionClosedException as e:
        sock.close()                                    # ソケットの切断
        break                                           # while sockを抜ける
    date = datetime.datetime.today()                    # 日付を取得
    print(date.strftime('%Y/%m/%d %H:%M'), end='')      # 日付を出力
    try:
        res_dict = json.loads(payload)                  # 辞書型変数へ代入
    except Exception:
        print(',', payload)                             # 受信データを出力
        continue                                        # whileの先頭に戻る
    for key in keys:                                    # 受信項目を繰り返し処理
        val = res_dict.get(key)                         # 辞書型変数から索引検索
        if val is not None:                             # 指定項目がある時
            val = str(val).strip()                      # 文字列変換と両端処理
            print(',', key, '=', val, end='')           # 値を表示
    print()                                             # 改行

'''
pi@raspberrypi:~/iot/learning $ ./example33_ws_aws.py
WebSocket Logger
Listening, wss://w1za4078ci.execute-api.us-west-2.amazonaws.com/Prod
2019/10/06 18:48, type = keepalive, sockets = 3
2019/10/06 18:50, type = keepalive, sokets = 3
2019/10/06 18:51, type = notify, sokets = 4, total = 68
2019/10/06 18:52, type = keepalive, sokets = 4
2019/10/06 18:52, type = message, data = ホームページを更新しました
2019/10/06 18:54, type = keepalive, sokets = 4
2019/10/06 18:55, type = message, data = 36.5
2019/10/06 18:56, type = keepalive, sokets = 4
'''
