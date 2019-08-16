#!/usr/bin/env python3
# coding: utf-8

# Raspberry Pi用
# micro:bitのシリアルを受信し、Ambientへ送信する
# Copyright (c) 2019 Wataru KUNINO

ambient_chid='0000'                 # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef'     # ここにはライトキーを入力
amdient_tag='d1'                    # データ番号d1～d8のいずれかを入力
ambient_interval = 30               # Ambientへの送信間隔
dev_name = 'temp0_3'                                    # UDP送信用デバイス名

import sys
import serial
import socket
import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import time

buf_n= 128                                              # 受信バッファ容量(バイト)
url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey, amdient_tag:0.0}  # 内容を変数body_dictへ
ambient_time = 0                                        # 次回の送信時刻 UTC

print('Serial Logger (usage: '+sys.argv[0]+' /dev/ttyACMx)')       # タイトル表示
argc = len(sys.argv)                                    # 引数の数をargcへ代入
if argc >= 2:                                           # 入力パラメータ数の確認
    port = sys.argv[1]                                  # ポート名を設定
else:
    port = '/dev/ttyACM0'

try:
    com = serial.Serial(port, 115200, timeout = 0.05)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while com and sock:
    rx = com.read(buf_n)
    if len(rx) == 0:
        continue
    rx = rx.decode()
    s=''                                                # 表示用の文字列変数s
    for c in rx:
        if ord(c) >= ord(' ') and ord(c) <= ord('~'):   # 表示可能文字
            s += c                                      # 文字列sへ追加
    print(s)

    if s[0:4] != 'Rx: ' and len(s) < 6:                 # 「Rx:」以外の時
        continue

    # UDP送信
    try:
        val = int(s[4:])
    except ValueError:
        val = 0
    udp = dev_name + ',' + str(val)
    print('send : ' + udp)                          # 受信データを出力
    udp=(udp + '\n').encode()                       # 改行追加とバイト列変換
    sock.sendto(udp,('255.255.255.255',1024))       # UDPブロードキャスト送信

    # Ambientへ送信
    utc = time.time()
    if int(ambient_chid) == 0 or utc < ambient_time:
        continue
    ambient_time = utc + ambient_interval
    body_dict[amdient_tag] = val
    print(head_dict)                                # 送信ヘッダhead_dictを表示
    print(body_dict)                                # 送信内容body_dictを表示
    post = urllib.request.Request(url_s, json.dumps(body_dict).encode(), head_dict)
                                                    # POSTリクエストデータを作成
    try:                                            # 例外処理の監視を開始
        res = urllib.request.urlopen(post)          # HTTPアクセスを実行
    except Exception as e:                          # 例外処理発生時
        print(e,url_s)                              # エラー内容と変数url_sを表示
        continue
    res_str = res.read().decode()                   # 受信テキストを変数res_strへ
    res.close()                                     # HTTPアクセスの終了
    if len(res_str):                                # 受信テキストがあれば
        print('Response:', res_str)                 # 変数res_strの内容を表示
    else:
        print('Done')                               # Doneを表示
sock.close()                                        # ソケットの切断
com.close()
