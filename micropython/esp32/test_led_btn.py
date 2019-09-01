# coding: utf-8
# ESP32マイコンの動作確認 Lチカ＋ボタン操作
# 0.5秒おきにLEDの点灯と消灯を反転し、ボタンが押されている間は高速点滅する
# Copyright (c) 2019 Wataru KUNINO

from machine import Pin                 # ライブラリmachineのPinを組み込む
from time import sleep                  # ライブラリtimeからsleepを組み込む

led = Pin(2, Pin.OUT)                   # GPIO出力用インスタンスledを生成
btn = Pin(0, Pin.IN)                    # GPIO入力用インスタンスbtnを生成

while True:                             # 繰り返し処理
    b = led.value()                     # 現在のLEDの状態を変数bへ代入
    b = int(not(b))                     # 変数bの値を論理反転(0→1、1→0)
    print('LED =',b)                    # 変数bの値を表示
    led.value(b)                        # 変数bの値をLED出力
    sleep(0.5)                          # 0.5秒間の待ち時間処理(低速点滅)
    while btn.value() == 0:             # ボタンが押されている間の繰り返し
        led.value(not led.value())      # 現在のLED出力を反転して出力
        print('.', end="")              # 「.」表示
        sleep(0.1)                      # 0.1秒だけ待つ(高速点滅)
