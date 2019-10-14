#!/usr/bin/env python3
# coding: utf-8

# Raspberry Pi用
# ESP32のシリアルを受信する
# Copyright (c) 2019 Wataru KUNINO

import sys
import serial

buf_n= 1024                                             # 受信バッファ容量(バイト)
argc = len(sys.argv)                                    # 引数の数をargcへ代入

print('Serial Logger (usage: '+sys.argv[0]+' /dev/ttyUSBx)')       # タイトル表示
if argc >= 2:                                           # 入力パラメータ数の確認
    port = sys.argv[1]                                  # ポート名を設定
else:
    port = '/dev/ttyUSB0'

try:
    com = serial.Serial(port, 115200, timeout = 0.01)
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while com:
    rx = com.read(buf_n)
    if len(rx) == 0:
        continue
    if len(rx) > buf_n - 1:
        print('buffer over run, len =',len(rx))
        continue
    try:
        rx = rx.decode()
    except Exception as e:                              # 例外処理発生時
        print('ERROR:',e)                               # エラー内容を表示
        continue
    s=''                                                # 表示用の文字列変数s
    for c in rx:
        if ord(c) >= ord(' ') and ord(c) <= ord('~') or ord(c) == ord('\n'):
            s += c                                      # 文字列sへ追加
    print(s,end='')
com.close()

##### ToDo
# UnicodeDecodeError: 'utf-8' codec can't decode bytes in position 94-95: unexpected end of data