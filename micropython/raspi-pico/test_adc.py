# Raspberry Pi の動作確認 ADC入力に応じてLEDの輝度を変更
# Copyright (c) 2022 Wataru KUNINO

from machine import ADC,Pin,PWM         # ライブラリmachineのADCを組み込む
from utime import sleep                 # μtimeからsleepを組み込む

freq = 1000
window = 1024
sample_wait = 1 / freq

led = PWM(Pin(25, Pin.OUT))             # PWM出力用インスタンスledを生成
led.freq(60)
adc1 = ADC(1)                           # ADCポート1(Pin32)用adc1を生成

while True:                             # 繰り返し処理
    valSum = 0
    for i in range(window):
        adc = adc1.read_u16()
        valSum += adc
        sleep(sample_wait)             # 待ち時間処理
    valDc = int(valSum / window + 0.5)
    voltDc = valDc * 3300 / 65535      # ADC値を電圧(mV)に変換
    print(voltDc)
    led.duty_u16(valDc)                # LEDを点灯する
