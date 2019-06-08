#!/usr/bin/env python3
# coding: utf-8
# Example 11 Lチカ

port = 4                                # GPIO ポート番号

from RPi import GPIO                    # ライブラリRPi内のGPIOモジュールの取得
from time import sleep                  # スリープ実行モジュールの取得
from sys import argv                    # 本プログラムの引数argvを取得する

print(argv[0])                          # プログラム名を表示する
if len(argv) >= 2:                      # 引数があるとき
    port = int(argv[1])                 # 整数としてportへ代入
GPIO.setmode(GPIO.BCM)                  # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)              # ポート番号portのGPIOを出力に設定

try:                                    # キー割り込みの監視を開始
    while True:                         # 繰り返し処理
        b = GPIO.input(port)            # 現在のGPIOの状態を変数bへ代入
        b = int(not(b))                 # 変数bの値を論理反転
        print('GPIO'+str(port),'=',b)   # ポート番号と変数bの値を表示
        GPIO.output(port, b)            # 変数bの値をGPIO出力
        sleep(0.5)                      # 0.5秒間の待ち時間処理
except KeyboardInterrupt:               # キー割り込み発生時
    print('\nKeyboardInterrupt')        # キーボード割り込み表示
    GPIO.cleanup(port)                  # GPIOを未使用状態に戻す
    exit()
