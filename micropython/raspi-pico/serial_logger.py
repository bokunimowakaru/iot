#!/usr/bin/env python3
# coding: utf-8

# Raspberry Pi用
# micro:bitのシリアルを受信する
# Copyright (c) 2019 Wataru KUNINO

import sys
import serial

buf_n= 128                                              # 受信バッファ容量(バイト)
argc = len(sys.argv)                                    # 引数の数をargcへ代入

print('Serial Logger (usage: '+sys.argv[0]+' /dev/ttyACMx)')       # タイトル表示
if argc >= 2:                                           # 入力パラメータ数の確認
    port = sys.argv[1]                                  # ポート名を設定
else:
    port = '/dev/ttyACM0'

try:
    com = serial.Serial(port, 115200, timeout = 0.01)
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while com:
    rx = com.read(buf_n)
    if len(rx) == 0:
        continue
    rx = rx.decode()
    s=''                                                # 表示用の文字列変数s
    for c in rx:
        if ord(c) >= ord(' ') and ord(c) <= ord('~'):   # 表示可能文字
            s += c                                      # 文字列sへ追加
    print(s)
com.close()
