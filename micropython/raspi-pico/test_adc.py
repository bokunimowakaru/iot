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

'''
Raspberry Pi Picoに本プログラムを書き込み、Raspberry Piでシリアル受信すると
Picoで読み取った電圧をRaspberry Piで表示できます。

接続図

  電圧 ----32番ピン----> Raspberry Pi Pico ----USB----> Rasberry Pi

シリアル受信用プログラムを実行した時のようす

pi@raspberry:~/iot/micropython/raspi-pico $ ./serial_logger.py
Serial Logger (usage: ./serial_logger.py /dev/ttyACMx)
53.17464
53.225
'''
