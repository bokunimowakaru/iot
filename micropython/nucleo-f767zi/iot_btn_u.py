# coding: utf-8
# IoTボタンμ for MicroPython (よりメモリの節約が可能なusocketを使用)
# Copyright (c) 2018-2019 Wataru KUNINO

udp_to = '255.255.255.255'                  # UDPブロードキャストアドレス
udp_port = 1024                             # UDPポート番号

import network                              # ネットワーク通信ライブラリ
import usocket                              # μソケット通信ライブラリ
#      ~~~~~~~
pyb.LED(1).on()                             # LED(緑色)を点灯
eth = network.Ethernet()                    # Ethernetのインスタンスethを生成
try:                                        # 例外処理の監視を開始
    eth.active(True)                        # Ethernetを起動
    eth.ifconfig('dhcp')                    # DHCPクライアントを設定
except Exception as e:                      # 例外処理発生時
    pyb.LED(3).on()                         # LED(赤色)を点灯
    while True:
        print(e)                            # エラー内容を表示
        pyb.delay(3000)                     # 3秒の待ち時間処理

b = 0                                       # ボタン状態を保持する変数bの定義
sw = pyb.Switch()
while True:                                 # 繰り返し処理
    while b == sw():                        # キーの変化待ち
        pyb.delay(100)                      # 0.1秒間の待ち時間処理
    b = int(not( b ))                       # 変数bの値を論理反転
    if b == 1:                              # b=0:ボタン押下時
        pyb.LED(2).on()                     # LED(青色)を点灯
        udp_s = 'Ping'                      # 変数udp_sへ文字列「Ping」を代入
    else:                                   # b=1:ボタン開放時
        pyb.LED(2).off()                    # LED(青色)を消灯
        udp_s = 'Pong'                      # 変数udp_sへ文字列「Pong」を代入
    print('B1 User', '=', b, udp_s)         # 変数b、udp_sの値を表示

    sock = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM) # μソケット作成
    #      ~~~~~~~        ~~~~~~~         ~~~~~~~
    udp_bytes = (udp_s + '\n').encode()                 # バイト列に変換

    try:
        sock.sendto(udp_bytes,(udp_to,udp_port))        # UDPブロードキャスト送信
    except Exception as e:
        print(e)                                        # エラー内容を表示

    sock.close()                                        # ソケットの切断
