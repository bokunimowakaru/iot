#!/usr/bin/env python3
# coding: utf-8
# Example 15 Raspberry Piを使ったIoT 温度計

filename = '/sys/class/thermal/thermal_zone0/temp'      # 温度ファイル
port     = 1024                                         # UDPポート番号を1024に
device_s = 'temp._3'                                    # デバイス識別名
intarval = 30                                           # 送信間隔（秒）

import socket                                           # ソケット通信ライブラリ
from sys import argv                                    # 引数argv取得モジュール
from time import sleep                                  # スリープ実行モジュール

if len(argv) == 2:                                      # 入力パラメータ数の確認
    if argv[1] > 0 and argv[1] < 65536:                 # ポート1～65535の時
        port = argv[1]                                  # 引数1をUDPポート番号に

while True:
    try:                                                # 例外処理の監視を開始
        fp = open(filename)                             # 温度ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
        sleep(60)                                       # 60秒間の停止
        continue                                        # whileに戻る

    temp_f = float(fp.read()) / 1000                    # 温度値tempの取得
    temp_i = round(temp_f)                              # 整数に変換してtemp_iへ
    fp.close()                                          # ファイルを閉じる
    print('Temperature =',temp_i,'('+str(temp_f)+')')   # 温度値を表示する

    try:                                                # ソケット作成部
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # 作成
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)   # 接続
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
        sleep(60)                                       # 60秒間の停止
        continue                                        # whileに戻る

    udp_s = device_s + ', ' + str(temp_i)               # 表示用の文字列変数udp
    print('send :', udp_s)                              # 受信データを出力
    udp_bytes = (udp_s + '\n').encode()                 # バイト列に変換
    sock.sendto(udp_bytes,('255.255.255.255',port))     # UDPブロードキャスト送信
    sock.close()                                        # ソケットの切断
    sleep(intarval)                                     # 送信間隔の待ち時間処理
