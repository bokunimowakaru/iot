#!/usr/bin/env python3
# coding: utf-8
# Example 12 カラー Lチカ

################################################################################
## ご注意：
## 本プログラムは Raspberry Pi 5 に対応するために、GPIO用ライブラリにGPIO Zeroを
## 使用します。
## Raspberry Pi 4 以前でも動作します。
## 書籍「Pythonで作るIoTシステム プログラム・サンプル集」のリストからの変更点は
## 変更前を各行の先頭の#で示し、変更後を各行のコメントの##で示します。
## 書籍と同じプログラムは、プログラム名に「_rpi」を付与して収録してあります。
################################################################################

port_R = 17                             # 赤色LED用 GPIO ポート番号
port_G = 27                             # 緑色LED用 GPIO ポート番号
port_B = 22                             # 青色LED用 GPIO ポート番号

ports = [port_R, port_G, port_B]
colors= ['消灯','赤色','緑色','黄色','青色','赤紫色','藍緑色','白色']
color = colors.index('白色')            # 初期カラー番号の取得（白色=7）

# from RPi import GPIO                  # ライブラリRPi内のGPIOモジュールの取得
from gpiozero import LED                ## GPIO ZeroのI/Oモジュール取得
from signal import pause                # シグナル待ち受けの取得
from sys import argv                    # 本プログラムの引数argvを取得する

print(argv[0])                          # プログラム名を表示する
if len(argv) >= 2:                      # 引数があるとき
    color = int(argv[1])                # 色番号を変数colorへ代入

# GPIO.setmode(GPIO.BCM)                # ポート番号の指定方法の設定
# GPIO.setwarnings(False)               # ポート使用中などの警告表示を無効に
leds = list()                           ## LEDインスタンス用

for port in ports:                      # 各ポート番号を変数portへ代入
    # GPIO.setup(port, GPIO.OUT)        # ポート番号portのGPIOを出力に設定
    leds.append(LED(port))              ## GPIO ZeroのLEDを実体化

color %= len(colors)                    # 色数(8色)に対してcolorは0～7
print('Color =',color,colors[color])    # 色番号と色名を表示

for i in range( len(leds) ):            # 各ポート番号の参照indexを変数iへ
    port = ports[i]                     # ポート番号をportsから取得
    b = (color >> i) & 1                # 該当LEDへの出力値を変数bへ
    print('GPIO'+str(port),'=',b)       # ポート番号と変数bの値を表示
    # GPIO.output(port, b)              # ポート番号portのGPIOを出力に設定
    leds[i].value = b                   ## ↑
print('[Ctrl]+[C]で終了します')
pause()                                 ## 待ち受け待機する(永久ループ)
