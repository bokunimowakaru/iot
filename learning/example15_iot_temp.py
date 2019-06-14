#!/usr/bin/env python3
# coding: utf-8
# Example 15 Raspberry Piを使ったIoT 温度計

filename = '/sys/class/thermal/thermal_zone0/temp'      # 温度ファイル
udp_to = '255.255.255.255'                              # UDPブロードキャスト
udp_port = 1024                                         # UDPポート番号
device_s = 'temp._3'                                    # デバイス識別名
interval = 30                                           # 送信間隔（秒）
temp_offset = 17.8                                      # CPUの温度上昇値(要調整)

import socket                                           # ソケット通信ライブラリ
from time import sleep                                  # スリープ実行モジュール

while True:
    try:                                                # 例外処理の監視を開始
        fp = open(filename)                             # 温度ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
        sleep(60)                                       # 60秒間の停止
        continue                                        # whileに戻る

    temp_f = float(fp.read()) / 1000 - temp_offset      # 温度値tempの取得
    temp_i = round(temp_f)                              # 整数に変換してtemp_iへ
    fp.close()                                          # ファイルを閉じる
    print('Temperature =',temp_i,'('+str(temp_f)+')')   # 温度値を表示する

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # ソケット作成
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)   # ソケット設定

    udp_s = device_s + ', ' + str(temp_i)               # 表示用の文字列変数udp
    print('send :', udp_s)                              # 受信データを出力
    udp_bytes = (udp_s + '\n').encode()                 # バイト列に変換

    try:                                                # 作成部
        sock.sendto(udp_bytes,(udp_to,udp_port))        # UDPブロードキャスト送信

    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示

    sock.close()                                        # ソケットの切断
    sleep(interval)                                     # 送信間隔の待ち時間処理
