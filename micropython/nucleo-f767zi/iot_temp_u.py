# coding: utf-8
# IoT 温度計μ for MicroPython (よりメモリの節約が可能なusocketを使用)
# Copyright (c) 2018-2019 Wataru KUNINO

# Error ENOMEM や EADDRINUSE が出た場合はハードウェアリセットを実行してください
#   machine.reset()

udp_to = '255.255.255.255'                              # UDPブロードキャスト
udp_port = 1024                                         # UDPポート番号
device_s = 'temp._3'                                    # デバイス識別名
interval = 10                                           # 送信間隔（秒）
temp_offset = 8.0                                       # CPU温度上昇値(要調整)

import network                                          # ネットワーク通信
import usocket                                          # μソケット通信
#      ~~~~~~~
pyb.LED(1).on()                                         # LED(緑色)を点灯
eth = network.Ethernet()                                # Ethernet用のethを生成
try:                                                    # 例外処理の監視を開始
    eth.active(True)                                    # Ethernetを起動
    eth.ifconfig('dhcp')                                # DHCPクライアントを設定
except Exception as e:                                  # 例外処理発生時
    pyb.LED(3).on()                                     # LED(赤色)を点灯
    while True:
        print(e)                                        # エラー内容を表示
        pyb.delay(3000)                                 # 3秒の待ち時間処理

adc = pyb.ADC(16)                                       # 温度用のADC 16を生成
while True:
    pyb.LED(2).on()                                     # LED(青色)を点灯
    temp = 25 + 400 * (3.3 * adc.read() / 4096 - 0.76)  # 温度を取得
    temp -= temp_offset                                 # temp_offsetを減算
    temp_i = round(temp)                                # 整数に変換してtemp_iへ
    print('Temperature =',temp_i,'('+str(temp)+')')     # 温度値を表示する

    sock = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM) # μソケット作成
    #      ~~~~~~~        ~~~~~~~         ~~~~~~~
    udp_s = device_s + ', ' + str(temp_i)               # 表示用の文字列変数udp
    print('send :', udp_s)                              # 受信データを出力
    udp_bytes = (udp_s + '\n').encode()                 # バイト列に変換

    try:
        sock.sendto(udp_bytes,(udp_to,udp_port))        # UDPブロードキャスト送信

    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示

    sock.close()                                        # ソケットの切断
    pyb.LED(2).off()                                    # LED(青色)を消灯
    pyb.delay(interval * 1000)                          # 送信間隔の待ち時間処理
