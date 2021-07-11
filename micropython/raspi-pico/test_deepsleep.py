# Raspberry Pi Pico の動作確認 Lチカ＋ログ出力表示
# 0.5秒おきにLEDの点灯と消灯を反転する
# Copyright (c) 2021 Wataru KUNINO

from machine import Pin                 # ライブラリmachineのPinを組み込む
from machine import deepsleep,lightsleep
from utime import sleep

sleep_duration = 1                      # スリープ時間（秒）

class sleepmode:
    mode_sleep = 0
    mode_lightsleep = 1
    mode_deepsleep = 2
    mode_name = ['sleep','lightsleep','deepsleep']

def goto_sleep(mode):
    print('LED =',led.value(),end=', ')
    print('Sleep Mode =',sleepmode.mode_name[mode])
    if mode == sleepmode.mode_sleep:
        sleep(sleep_duration)           # 待ち時間処理 utime.sleep
    if mode == sleepmode.mode_lightsleep:
        lightsleep(sleep_duration)      # 待ち時間処理 machine.lightsleep
    if mode == sleepmode.mode_deepsleep:
        deepsleep(sleep_duration)       # 待ち時間処理 machine.deepsleep

mode = sleepmode.mode_sleep
led = Pin(25, Pin.OUT)                  # GPIO出力用インスタンスledを生成

while True:                             # 繰り返し処理
    led.value(0)                        # 変数bの値をLED出力
    goto_sleep(mode)
    led.value(1)                        # 変数bの値をLED出力
    goto_sleep(mode)
    
