# Raspberry Pi の動作確認 I2C LCDに文字を表示する
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

from machine import Pin,I2C             # ライブラリmachineのI2Cを組み込む
from utime import sleep                 # μtimeからsleepを組み込む

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

def i2c_lcd_out(y, text):
    if y == 0:
        i2c.writeto_mem(aqm1602, 0x00, b'\x80')    # 1行目
    else:
        i2c.writeto_mem(aqm1602, 0x00, b'\xC0')    # 2行目
    i2c.writeto_mem(aqm1602, 0x40, bytearray(text))       # 文字出力

i2c_lcd_out(0,'Hello!  I2C LCD')
i2c_lcd_out(1,'by Wataru Kunino')
