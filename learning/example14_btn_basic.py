#!/usr/bin/env python3
# coding: utf-8
# Example 14 ボタン BASIC

################################################################################
## ご注意：
## 本プログラムは Raspberry Pi 5 に対応するために、GPIO用ライブラリにGPIO Zeroを
## 使用します。
## Raspberry Pi 4 以前でも動作します。
## 書籍「Pythonで作るIoTシステム プログラム・サンプル集」のリストからの変更点は
## 変更前を各行の先頭の#で示し、変更後を各行のコメントの##で示します。
## 書籍と同じプログラムは、プログラム名に「_rpi」を付与して収録してあります。
################################################################################

port = 26                               # GPIO ポート番号
b = 0                                   # GPIO 出力値

# from RPi import GPIO                  # ライブラリRPi内のGPIOモジュールの取得
from gpiozero import Button             ## ライブラリgpiozeroのButtonを取得
from time import sleep                  # スリープ実行モジュールの取得

# GPIO.setmode(GPIO.BCM)                # ポート番号の指定方法の設定
# GPIO.setwarnings(False)               # ポート使用中などの警告表示を無効に
# GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO 26 を入力に設定
btn = Button(port)                      ## ポートportをボタン入力に

while True:                             # 繰り返し処理
    # b = GPIO.input(port)              # GPIO入力値を変数bへ代入
    b = int(not btn.value)              ## ↑
    print('GPIO'+str(port),'=',b)       # ポート番号と変数bの値を表示
    sleep(0.5)                          # 0.5秒間の待ち時間処理
