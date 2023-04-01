###############################################################################
# Raspberry Pi Pico / Pico W の動作確認 Lチカ＋ログ出力表示
###############################################################################
# 5秒おきにスリープ状態を推移します。推移時にLEDの点滅で状態変更を示します。
#
# LED表示      Num.  スリープ状態
# －－－－－    0    sleep (通常)
# ･－･－･－･－  -    sleep (通常)
# ･－－－－     1    lightsleep (ライトスリープ)
# ･－･－･－･－  -    sleep (通常)
# ･･－－－      2    deepsleep (ディープスリープ)
# ･－･－･－･－  -    sleep (通常)
#
#                                         Copyright (c) 2021-2023 Wataru KUNINO
###############################################################################

from machine import Pin                 # ライブラリmachineのPinを組み込む
from machine import deepsleep,lightsleep
from utime import sleep

sleep_duration = 5                      # スリープ時間（秒）

class sleepmode:
    num = 3
    mode_sleep = 0
    mode_lightsleep = 1
    mode_deepsleep = 2
    mode_name = ['sleep','lightsleep','deepsleep']

def goto_sleep(mode):
    print('Sleep Mode =',sleepmode.mode_name[mode])
    sleep(0.1)
    if mode == sleepmode.mode_sleep:
        sleep(sleep_duration)           # 待ち時間処理 utime.sleep
    if mode == sleepmode.mode_lightsleep:
        lightsleep(sleep_duration*1000) # 待ち時間処理 machine.lightsleep
    if mode == sleepmode.mode_deepsleep:
        deepsleep(sleep_duration*1000)  # 待ち時間処理 machine.deepsleep

def led_disp(n):                        # LEDの点滅で数字を示す 0～9
    for i in range(1,6):
        led.value(1)
        if n<0 or n>9:
            sleep(0.2 if i%2 else 0.6)  # i%2 ? 0.2 : 0.6
        elif i <= n%5:
            sleep(0.2 if n<=5 else 0.6) # n<=5 ? 0.2 : 0.6
        else:
            sleep(0.6 if n<=5 else 0.2) # n<=5 ? 0.6 : 0.2
        led.value(0)
        sleep(0.2)
    if n<0 or n>9:
        led.value(1)
        sleep(0.6)
        led.value(0)
    sleep(0.6)

try:
    led = Pin("LED", Pin.OUT)           # GPIO出力用ledを生成(Pico W 用)
except TypeError:
    led = Pin(25, Pin.OUT)              # GPIO出力用ledを生成(Pico 用)

for mode in range(sleepmode.num):
   led_disp(mode)                       # スリープ番号0～2をLEDの点滅で出力
   goto_sleep(mode)
   led_disp(-1)                         # LEDの点滅でスリープ終了を出力
   sleep(5)

###############################################################################
# 以下は実行されない
mode = sleepmode.mode_deepsleep
goto_sleep(mode)
exit()
