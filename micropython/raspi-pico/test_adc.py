# Raspberry Pi の動作確認 ADC入力に応じてLEDの輝度を変更
# Copyright (c) 2022 Wataru KUNINO

from machine import ADC,Pin,PWM         # ライブラリmachineのADCを組み込む
from utime import sleep                 # μtimeからsleepを組み込む

freq = 40000
window = 1024
display = 'AC'
sample_wait = 1 / freq

led = PWM(Pin(25, Pin.OUT))             # PWM出力用インスタンスledを生成
led.freq(60)
adc0 = ADC(0)                           # ADCポート0(Pin31)用adc0を生成

peak_i = 0
peakLv = 0
while True:                             # 繰り返し処理
    vals = []
    valSum = 0
    for i in range(window):
        adc = adc0.read_u16()
        valSum += adc
        vals.append(adc)               # ADCから値を取得して変数valに代入
        sleep(sample_wait)             # 待ち時間処理
    valDc = int(valSum / window + 0.5)
    acSum = 0
    for i in range(window):
        acSum += abs(vals[i] - valDc)
    valAc = int(acSum / window + 0.5)
    voltDc = valDc * 3300 / 65535  # ADC値を電圧(mV)に変換
    voltAc = valAc * 3300 / 65535  # ADC値を電圧(mV)に変換
    peak_i += 1
    if peak_i > 100:
        peakLv = voltAc
        peak_i = 0
    if peakLv < voltAc:
        peakLv = voltAc
    if display == 'DC':
        print('Voltage DC =', voltDc)
        led.duty_u16(valDc)                   # LEDを点灯する
    if display == 'AC':
        print('Voltage AC =', voltAc, 'Peak =', peakLv)
        led.duty_u16(valAc)                   # LEDを点灯する
