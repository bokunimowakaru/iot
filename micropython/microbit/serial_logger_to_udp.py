#!/usr/bin/env python3
# coding: utf-8

# Raspberry Pi用
# micro:bitのシリアルを受信し、UDP送信する
# Copyright (c) 2019 Wataru KUNINO

dev_name = 'temp0_3'                                    # UDP送信用デバイス名

import sys
import serial
import socket

buf_n= 128                                              # 受信バッファ容量(バイト)

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

    if s[0:4] == 'Rx: ' and len(s) >= 6:                # Rx:を受信したとき
        try:
            val = int(s[4:])
        except ValueError:
            val = 0
        udp = dev_name + ',' + str(val)
        print('send : ' + udp)                          # 受信データを出力
        udp=(udp + '\n').encode()                       # 改行追加とバイト列変換
        sock.sendto(udp,('255.255.255.255',1024))       # UDPブロードキャスト送信
sock.close()                                            # ソケットの切断
com.close()
