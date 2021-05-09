# Raspberry Pi の動作確認 温度を測定し表示する
# Copyright (c) 2021 Wataru KUNINO

from machine import ADC,Pin             # ライブラリmachineのADCを組み込む
from utime import sleep                 # μtimeからsleepを組み込む

led = Pin(25, Pin.OUT)                  # GPIO出力用インスタンスledを生成
adc = ADC(4)                            # 温度センサ用ADCポートadcを生成
prev = 0                                # 前回の温度値を保持するための変数
while True:                             # 繰り返し処理
    val = adc.read_u16()                # ADCから値を取得して変数valに代入
    mv = val * 3300 / 65535             # ADC値を電圧(mV)に変換
    temp = 27 - (mv - 706) / 1.721      # ADC電圧値を温度(℃)に変換
    print('Temperature =',round(temp,1))# 温度値を表示
    if temp > prev:                     # 前回の温度値よりも大きいとき
        led.value(1)                    # LEDを点灯する
    else:                               # そうでないとき(前回値以下)
        led.value(0)                    # LEDを消灯する
    prev = temp                         # 変数prevに前回値を保持する
    sleep(5)                            # 5秒間の待ち時間処理
