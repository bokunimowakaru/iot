#!/usr/bin/env python3
# coding: utf-8
# Example 14 Raspberry Piを使った IoTボタン

################################################################################
## ご注意：
## 本プログラムは Raspberry Pi 5 に対応するために、GPIO用ライブラリにGPIO Zeroを
## 使用します。
## Raspberry Pi 4 以前でも動作します。
## 書籍「Pythonで作るIoTシステム プログラム・サンプル集」のリストからの変更点は
## 変更前を各行の先頭の#で示し、変更後を各行のコメントの##で示します。
## 書籍と同じプログラムは、プログラム名に「_rpi」を付与して収録してあります。
################################################################################

port = 26                                   # GPIO ポート番号
udp_to = '255.255.255.255'                  # UDPブロードキャストアドレス
udp_port = 1024                             # UDPポート番号

import socket                               # ソケット通信ライブラリ
# from RPi import GPIO                      # RPi内のGPIOモジュールの取得
from gpiozero import Button                 ## ライブラリgpiozeroのButtonを取得
from time import sleep                      # スリープ実行モジュールの取得
from sys import argv                        # 本プログラムの引数argvを取得

print(argv[0])                              # プログラム名を表示する
if len(argv) >= 2:                          # 引数があるとき
    port = int(argv[1])                     # 整数としてportへ代入
# GPIO.setmode(GPIO.BCM)                    # ポート番号の指定方法の設定
# GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO 26 を入力に設定
btn = Button(port)                          ## ポートportをボタン入力に

b = 1                                       # ボタン状態を保持する変数bの定義
while True:                                 # 繰り返し処理
    try:                                    # キー割り込みの監視を開始
        # while b == GPIO.input(port):      # キーの変化待ち
        while b == int(not btn.value):      ## ↑
            sleep(0.1)                      # 0.1秒間の待ち時間処理
    except KeyboardInterrupt:               # キー割り込み発生時
        print('\nKeyboardInterrupt')        # キーボード割り込み表示
        # GPIO.cleanup(port)                # GPIOを未使用状態に戻す
        btn.close()                         ## ↑
        exit()
    b = int(not( b ))                       # 変数bの値を論理反転
    if b == 0:                              # b=0:ボタン押下時
        udp_s = 'Ping'                      # 変数udp_sへ文字列「Ping」を代入
    else:                                   # b=1:ボタン開放時
        udp_s = 'Pong'                      # 変数udp_sへ文字列「Pong」を代入
    print('GPIO'+str(port), '=', b, udp_s)  # ポート番号と変数b、udp_sの値を表示

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # ソケット作成
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)   # ソケット設定

    udp_bytes = (udp_s + '\n').encode()                 # バイト列に変換

    try:                                                # 作成部
        sock.sendto(udp_bytes,(udp_to,udp_port))        # UDPブロードキャスト送信
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示

    sock.close()                                        # ソケットの切断
