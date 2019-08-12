# coding: utf-8
# IoT 温度計 for MicroPython
# Copyright (c) 2018-2019 Wataru KUNINO

# Error ENOMEM や EADDRINUSE が出た場合はハードウェアリセットを実行してください
#   machine.reset()

udp_to = '255.255.255.255'                              # UDPブロードキャスト
udp_port = 1024                                         # UDPポート番号
device_s = 'temp._3'                                    # デバイス識別名
interval = 10                                           # 送信間隔（秒）
temp_offset = 8.0                                       # CPUの温度上昇値(要調整)

import network
import socket

pyb.LED(1).on()
eth = network.Ethernet()
try:
    eth.active(True)
    eth.ifconfig('dhcp')
except Exception as e:                                  # 例外処理発生時
    pyb.LED(3).on()
    while True:
        print(e)                                        # エラー内容を表示
        pyb.delay(3000)

adc = pyb.ADC(16)                                       # 温度用のADC 16を生成
while True:
    pyb.LED(2).on()
    temp = 25 + 400 * (3.3 * adc.read() / 4096 - 0.76)  # 温度を取得
    temp -= temp_offset
    temp_i = round(temp)                                # 整数に変換してtemp_iへ
    print('Temperature =',temp_i,'('+str(temp)+')')     # 温度値を表示する

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # ソケット作成
#   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)   # ソケット設定

    udp_s = device_s + ', ' + str(temp_i)               # 表示用の文字列変数udp
    print('send :', udp_s)                              # 受信データを出力
    udp_bytes = (udp_s + '\n').encode()                 # バイト列に変換

    try:                                                # 作成部
        sock.sendto(udp_bytes,(udp_to,udp_port))        # UDPブロードキャスト送信

    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示

    sock.close()                                        # ソケットの切断
    pyb.LED(2).off()
    pyb.delay(interval * 1000)                          # 送信間隔の待ち時間処理
