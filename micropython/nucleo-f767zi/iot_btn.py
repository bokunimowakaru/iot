# coding: utf-8
# IoTボタン for MicroPython
# Copyright (c) 2018-2019 Wataru KUNINO

udp_to = '255.255.255.255'                  # UDPブロードキャストアドレス
udp_port = 1024                             # UDPポート番号

import network
import socket                               # ソケット通信ライブラリ

pyb.LED(1).on()
eth = network.Ethernet()
try:
    eth.active(True)
    eth.ifconfig('dhcp')
except Exception as e:                      # 例外処理発生時
    pyb.LED(3).on()
    while True:
        print(e)                            # エラー内容を表示
        pyb.delay(3000)

b = 0                                       # ボタン状態を保持する変数bの定義
sw = pyb.Switch()
while True:                                 # 繰り返し処理
    while b == sw():                        # キーの変化待ち
        pyb.delay(100)                      # 0.1秒間の待ち時間処理
    b = int(not( b ))                       # 変数bの値を論理反転
    if b == 1:                              # b=0:ボタン押下時
        pyb.LED(2).on()
        udp_s = 'Ping'                      # 変数udp_sへ文字列「Ping」を代入
    else:                                   # b=1:ボタン開放時
        pyb.LED(2).off()
        udp_s = 'Pong'                      # 変数udp_sへ文字列「Pong」を代入
    print('B1 User', '=', b, udp_s)         # 変数b、udp_sの値を表示

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # ソケット作成
#   sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)   # ソケット設定

    udp_bytes = (udp_s + '\n').encode()                 # バイト列に変換

    try:                                                # 作成部
        sock.sendto(udp_bytes,(udp_to,udp_port))        # UDPブロードキャスト送信
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示

    sock.close()                                        # ソケットの切断