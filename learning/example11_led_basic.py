#!/usr/bin/env python3
# coding: utf-8
# Example 11 Lチカ BASIC

port = 4                                # GPIO ポート番号
b = 0                                   # GPIO 出力値

from RPi import GPIO                    # ライブラリRPi内のGPIOモジュールの取得
from time import sleep                  # スリープ実行モジュールの取得

GPIO.setmode(GPIO.BCM)                  # ポート番号の指定方法の設定
GPIO.setwarnings(False)                 # ポート使用中などの警告表示を無効に
GPIO.setup(port, GPIO.OUT)              # ポート番号portのGPIOを出力に設定

while True:                             # 繰り返し処理
    b = int(not(b))                     # 変数bの値を論理反転
    print('GPIO'+str(port),'=',b)       # ポート番号と変数bの値を表示
    GPIO.output(port, b)                # 変数bの値をGPIO出力
    sleep(0.5)                          # 0.5秒間の待ち時間処理
