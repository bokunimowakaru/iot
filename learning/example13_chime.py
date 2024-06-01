#!/usr/bin/env python3
# coding: utf-8
# Example 13 チャイム

port = 4                                # GPIO ポート番号
ping_f = 554                            # 周波数1
pong_f = 440                            # 周波数2

# from RPi import GPIO                  # ライブラリRPi内のGPIOモジュールの取得
from gpiozero import TonalBuzzer        ## GPIO Zero のTonalBuzzerを取得
from time import sleep                  # スリープ実行モジュールの取得
from sys import argv                    # 本プログラムの引数argvを取得する

print(argv[0])                          # プログラム名を表示する
if len(argv) >= 2:                      # 引数があるとき
    port = int(argv[1])                 # 整数としてportへ代入
# GPIO.setmode(GPIO.BCM)                # ポート番号の指定方法の設定
# GPIO.setup(port, GPIO.OUT)            # ポート番号portのGPIOを出力に設定
# pwm = GPIO.PWM(port, ping_f)          # PWM出力用のインスタンスを生成
pwm = TonalBuzzer(port)                 ## ↑

# pwm.start(50)                         # PWM出力を開始。デューティ50％
pwm.play(ping_f)                        ## ↑
sleep(0.3)                              # 0.3秒の待ち時間処理
# pwm.ChangeFrequency(pong_f)           # PWM周波数の変更
pwm.play(pong_f)                        ## ↑
sleep(0.3)                              # 0.3秒の待ち時間処理
pwm.stop()                              # PWM出力停止
#GPIO.cleanup(port)                     # GPIOを未使用状態に戻す
pwm.close()                             ## ↑
