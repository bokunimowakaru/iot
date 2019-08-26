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

addr = socket.getaddrinfo(host_s,80)[0][-1] # ホストのIPアドレスとポートを取得
sock = socket.socket()                      # ソケットのインスタンスを生成
sock.connect(addr)                          # ホストへのTCP接続を実行
req = 'GET ' + path_s + ' HTTP/1.0\r\n'     # HTTP GET命令を文字列変数reqへ代入
req += 'Host: ' + host_s + '\r\n\r\n'       # ホスト名を追記
sock.send(req.encode())                     # 変数reqをバイト列に変換してTCP送信

while True:                                 # HTTPヘッダ受信の繰り返し処理
    res = sock.readline().decode()          # 1行分の受信データを変数resへ代入
    print(res.strip())                      # 改行を削除して表示
    if res == '\n' or res == '\r\n':        # ヘッダの終了を検出
        break                               # ヘッダ終了時にwhileを抜ける

body = ''                                   # 文字列変数bodyの初期化
while True:                                 # HTTPコンテンツ部の受信処理
    res = sock.readline().decode().strip()  # 1行分の受信データを変数resへ代入
    if len(res) <= 0:                       # 受信データが無い時に
        break                               # 　　　　　　　whileループを抜ける
    body += res                             # コンテンツを変数bodyへ追記

print(body)                                 # 受信コンテンツを表示
res_dict = json.loads(body)                 # JSON形式のデータを辞書型に変換

print('--------------------------------------') # -----------------------------
print('title :', res_dict.get('title'))         # 項目'title'の内容を取得・表示
print('descr :', res_dict.get('descr'))         # 項目'descr'の内容を取得・表示
print('state :', res_dict.get('state'))         # 項目'state'の内容を取得・表示
print('url   :', res_dict.get('url'))           # 項目'url'内容を取得・表示
print('date  :', res_dict.get('date'))          # 項目'date'内容を取得・表示

pyb.LED(1).off()                                # LED(緑色)を消灯
