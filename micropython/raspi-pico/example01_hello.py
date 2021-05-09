# Raspberry Pi Pico の動作確認 Lチカ＋ログ出力表示
# 0.5秒おきにLEDの点灯と消灯を反転する
# Copyright (c) 2021 Wataru KUNINO

from machine import Pin                 # ライブラリmachineのPinを組み込む
from utime import sleep                 # μtimeからsleepを組み込む

led = Pin(25, Pin.OUT)                  # GPIO出力用インスタンスledを生成

while True:                             # 繰り返し処理
    b = led.value()                     # 現在のLEDの状態を変数bへ代入
    b = int(not(b))                     # 変数bの値を論理反転(0→1、1→0)
    print('Hello, world! LED =',b)      # 変数bの値を表示
    led.value(b)                        # 変数bの値をLED出力
    sleep(0.5)                          # 0.5秒間の待ち時間処理