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
import json                                     # JSON変換ライブラリを組み込む


url = 'wss://api.sakura.io/ws/v1/'
token = '00000000-0000-0000-0000-000000000000'         # sakura.ioのtokenを記入
argc = len(sys.argv)                                    # 引数の数をargcへ代入
print('WebSocket Logger (usage:',sys.argv[0],'token)') # タイトル表示
keepalive = 0

if argc == 2:                                           # 入力パラメータ数の確認
    token = sys.argv[1]                                # トークンを設定

url += token                                           # トークンを連結
print('Listening,',url)                                 # URL表示
sock = websocket.create_connection(url)                 # ソケットを作成
while sock:                                             # 作成に成功したとき
    res=sock.recv()                                     # WebSocketを取得
    date=datetime.datetime.today()                      # 日付を取得
    print(date.strftime('%Y/%m/%d %H:%M'), end='')      # 日付を出力
    print(', '+res)                                     # 受信データを出力
    res_dict = json.loads(res)                          # 辞書型の変数res_dictへ
    res_type = res_dict.get('type')                     # res_dict内のtypeを取得
    if res_type == 'keepalive':                         # typeがkeepaliveのとき
        if keepalive == 0:
            print('CONNECTED')
            keepalive=1
        continue
    if res_type != 'channels':                          # typeがchannelsでないとき
        continue
    res_id = res_dict.get('module')                     # res_dict内のmoduleを取得
    res_payload_dict = res_dict['payload']['channels']  # res_dict内のpayload取得
    print('from     =',res_id)
    data_text=''                                        # 受信テキスト用の文字列
    for data in res_payload_dict:                       # 各チャネルに対して
        data_type = data['type']
        data_ch   = data['channel']
        data_time  = data['datetime']
        data_type_s= 'Unknown'
        if data_type.lower() == 'i':
            data_type_s= 'Integer'
            data_value = data['value']
        if data_type == 'b':
            data_type_s= 'Binary'
            data_str   = data['value']
            i=0
            data_value=[]
            while i < len(data_str):                    # 受信16進数文字列の処理
                if i % 4 == 0:                          # リトルEndian 2バイト値
                    val = int(data_str[i+2:i+4] + data_str[i:i+2],16)
                    if val >= 32768:                    # 2補数の簡易処理
                        val -= 65536
                    data_value.append(val)              # 受信数値を配列変数へ
                c = chr(int(data_str[i:i+2],16))        # 文字コードへ変換
                if ord(c) >= 16 and ord(c) < 256:       # 特殊文字ではないとき
                    data_text += c                      # 文字列へ追加
                i += 2
        print('datetime =', data_time)
        print('channel  =', data_ch)
        print('type     =', data_type_s)
        print('value    =', data_value)                 # 受信結果(数値)の表示
    print('Message  =', data_text)                      # 受信結果(文字列)の表示
sock.close()                                            # ソケットの切断
