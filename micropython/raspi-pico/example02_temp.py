# coding: utf-8
# Raspberry Pi の動作確認 温度を測定し表示する
# Copyright (c) 2021 Wataru KUNINO

from machine import ADC,Pin             # ライブラリmachineのADCを組み込む
from time import sleep                  # ライブラリtimeからsleepを組み込む

led = Pin(25, Pin.OUT)                  # GPIO出力用インスタンスledを生成
adc = ADC(4)
prev = 0
while True:
    temp = 27 - (adc.read_u16() * 3300 / 65535 - 706) / 1.721
    print('Temperature =',round(temp,1))
    if temp > prev:
        led.value(1)
    else:
        led.value(0)
    prev = temp
    sleep(5)
