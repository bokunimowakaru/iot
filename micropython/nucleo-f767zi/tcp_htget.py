# coding: utf-8
# IoT連携の基本 HTTP GET for MicroPython
# Copyright (c) 2019 Wataru KUNINO

import network                              # ネットワーク通信ライブラリ
import socket                               # ソケット通信ライブラリ
import json                                 # JSON変換ライブラリを組み込む
from sys import exit                        # ライブラリsysからexitを組み込む

host_s = 'bokunimo.net'                     # アクセス先のホスト名
path_s = '/iot/cq/test.json'                # アクセスするファイルパス

pyb.LED(1).on()                             # LED(緑色)を点灯
eth = network.Ethernet()                    # Ethernetのインスタンスethを生成
try:                                        # 例外処理の監視を開始
    eth.active(True)                        # Ethernetを起動
    eth.ifconfig('dhcp')                    # DHCPクライアントを設定
except Exception as e:                      # 例外処理発生時
    print(e)                                # エラー内容を表示
    exit()

try:                                        # 例外処理の監視を開始
    addr = socket.getaddrinfo(host_s, 80)[0][-1]
    sock = socket.socket()
    sock.connect(addr)
    req = 'GET ' + path_s + ' HTTP/1.0\r\n'
    req += 'Host: ' + host_s + '\r\n\r\n'
    sock.send(req.encode())
except Exception as e:                      # 例外処理発生時
    print(e)                                # エラー内容を表示
    sock.close()
    exit()

body = '<head>'
while True:
    res = sock.readline().decode()
    if len(res) <= 0:
        break
    if res == '\n' or res == '\r\n':
        body = '<body>'
        break
    else:
        body = '<head>'
    print(res.strip())
if body != '<body>':
    print('no body data')
    sock.close()
    exit()

body = ''
while True:
    res = sock.readline().decode().strip()
    if len(res) <= 0:
        break
    body += res

print(body)

res_dict = json.loads(body)      # 受信データを変数res_dictへ代入
print('--------------------------------------') # -----------------------------
print('title :', res_dict.get('title'))         # 項目'title'の内容を取得・表示
print('descr :', res_dict.get('descr'))         # 項目'descr'の内容を取得・表示
print('state :', res_dict.get('state'))         # 項目'state'の内容を取得・表示
print('url   :', res_dict.get('url'))           # 項目'url'内容を取得・表示
print('date  :', res_dict.get('date'))          # 項目'date'内容を取得・表示

pyb.LED(1).off()                                # LED(緑色)を消灯
