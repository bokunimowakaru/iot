# Raspberry Pi の動作確認 ADC入力に応じてLEDの輝度を変更
# Copyright (c) 2022 Wataru KUNINO

# AE-AQM0802A, AE-AQM1602A, AQM1602Y 
##############################
# AQM1602 # Pico # GPIO
##############################
#     +V  #  5   # GP3
#    SDA  #  6   # GP4
#    SCL  #  7   # GP5
#    GND  #  8   # GND
##############################

# 参考文献
# https://github.com/bokunimowakaru/RaspberryPi/blob/master/libs/soft_i2c.c
# Copyright (c) 2014-2017 Wataru KUNINO https://bokunimo.net/raspi/

aqm1602 = 0x3E                          # LCD AQM1602のI2Cアドレス

from machine import ADC,Pin,PWM,I2C     # ライブラリmachineのADCを組み込む
from utime import sleep                 # μtimeからsleepを組み込む
from math import log10

freq = 40000
window = 1024
display = 'AC'
dispAcMaxMv = 1000
dispAcRangeDb = 40
sample_wait = 1 / freq

vdd = Pin(3, Pin.OUT)                   # GP3をAQM1602のV+ピンに接続
vdd.value(1)                            # V+用に3.3Vを出力
i2c = I2C(0, scl=Pin(5), sda=Pin(4))    # GP5をAQM1602のSCL,GP4をSDAに接続
i2c.writeto_mem(aqm1602, 0x00, b'\x39')    # IS=1
i2c.writeto_mem(aqm1602, 0x00, b'\x11')    # OSC
i2c.writeto_mem(aqm1602, 0x00, b'\x70')    # コントラスト	0
i2c.writeto_mem(aqm1602, 0x00, b'\x56')    # Power/Cont	6
i2c.writeto_mem(aqm1602, 0x00, b'\x6C')    # FollowerCtrl	C
sleep(0.2);
i2c.writeto_mem(aqm1602, 0x00, b'\x38')    # IS=0
i2c.writeto_mem(aqm1602, 0x00, b'\x0C')    # DisplayON	C

# font
i2c.writeto_mem(aqm1602, 0x00, b'\x40')    # CGRAM address 0x00
for i in range(7):
    i2c.writeto_mem(aqm1602, 0x40, b'\x1F')
i2c.writeto_mem(aqm1602, 0x40, b'\x00')

led = PWM(Pin(25, Pin.OUT))             # PWM出力用インスタンスledを生成
led.freq(60)
adc0 = ADC(0)                           # ADCポート0(Pin31)用adc0を生成

peak_i = 0
peakLv = 0
peakDb = 0
text = bytearray(16)
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
    if peak_i > 16:
        peakLv = voltAc
        peak_i = 0
    if peakLv < voltAc:
        peakLv = voltAc
        peakDb = int((20 * log10(voltAc/dispAcMaxMv) + dispAcRangeDb)/dispAcRangeDb * 17)
    if display == 'DC':
        level = int(valDc / 65536 * 17)
        for i in range(16):
            if i < level:
                text[i] = 0x00
            else:
                text[i] = 0xA5
            i2c.writeto_mem(aqm1602, 0x00, b'\x80')
            i2c.writeto_mem(aqm1602, 0x40, text)
        print('Voltage DC =', voltDc, 'Level =', level)
        i2c.writeto_mem(aqm1602, 0x00, b'\xC0')
        i2c.writeto_mem(aqm1602, 0x40, bytearray('DC = ' + str(int(voltDc)) + ' mV    '))
        led.duty_u16(valDc)                   # LEDを点灯する
    if display == 'AC':
        level = int((20 * log10(voltAc/dispAcMaxMv) + dispAcRangeDb)/dispAcRangeDb * 17)
        if level < 0:
            level = 0
        if level > dispAcRangeDb:
            level = dispAcRangeDb
        for i in range(16):
            if (i > 0 and i == peakDb) or i < level:
                text[i] = 0x00
            else:
                text[i] = 0xA5
            i2c.writeto_mem(aqm1602, 0x00, b'\x80')
            i2c.writeto_mem(aqm1602, 0x40, text)
        print('Voltage AC =', voltAc, 'Peak =', peakLv, 'Level =', level)
        i2c.writeto_mem(aqm1602, 0x00, b'\xC0')
        i2c.writeto_mem(aqm1602, 0x40, bytearray('AC = ' + str(int(peakLv)) + ' mV    '))
        led.duty_u16(valAc)                   # LEDを点灯する