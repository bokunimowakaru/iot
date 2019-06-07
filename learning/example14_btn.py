#!/usr/bin/env python3
# coding: utf-8
# Example 14 ボタン

port = 26                               # GPIO ポート番号

from RPi import GPIO                    # ライブラリRPi内のGPIOモジュールの取得
from time import sleep                  # スリープ実行モジュールの取得
from sys import argv                    # 本プログラムの引数argvを取得する

print(argv[0])                          # プログラム名を表示する
if len(argv) >= 2:                      # 引数があるとき
    port = int(argv[1])                 # 整数としてportへ代入
GPIO.setmode(GPIO.BCM)                  # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO 26 を入力に設定

try:                                    # キー割り込みの監視を開始
    while True:                         # 繰り返し処理
        b = GPIO.input(port)            # GPIO入力値を変数bへ代入
        print('GPIO'+str(port),'=',b)   # ポート番号と変数bの値を表示
        sleep(0.5)                      # 0.5秒間の待ち時間処理
except KeyboardInterrupt:               # キー割り込み発生時
    print('\nKeyboardInterrupt')        # キーボード割り込み表示
    GPIO.cleanup(port)                  # GPIOを未使用状態に戻す
    exit
