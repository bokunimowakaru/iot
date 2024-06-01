#!/usr/bin/env python3
# coding: utf-8
# Example 12 カラー Lチカ

port_R = 17                             # 赤色LED用 GPIO ポート番号
port_G = 27                             # 緑色LED用 GPIO ポート番号
port_B = 22                             # 青色LED用 GPIO ポート番号

ports = [port_R, port_G, port_B]
colors= ['消灯','赤色','緑色','黄色','青色','赤紫色','藍緑色','白色']
color = colors.index('白色')            # 初期カラー番号の取得（白色=7）

from RPi import GPIO                    # ライブラリRPi内のGPIOモジュール取得
from sys import argv                    # 本プログラムの引数argvを取得する

print(argv[0])                          # プログラム名を表示する
if len(argv) >= 2:                      # 引数があるとき
    color = int(argv[1])                # 色番号を変数colorへ代入

GPIO.setmode(GPIO.BCM)                  # ポート番号の指定方法の設定
GPIO.setwarnings(False)                 # ポート使用中などの警告表示を無効に
for port in ports:                      # 各ポート番号を変数portへ代入
    GPIO.setup(port, GPIO.OUT)          # ポート番号portのGPIOを出力に設定

color %= len(colors)                    # 色数(8色)に対してcolorは0～7
print('Color =',color,colors[color])    # 色番号と色名を表示

for i in range( len(ports) ):           # 各ポート番号の参照indexを変数iへ
    port = ports[i]                     # ポート番号をportsから取得
    b = (color >> i) & 1                # 該当LEDへの出力値を変数bへ
    print('GPIO'+str(port),'=',b)       # ポート番号と変数bの値を表示
    GPIO.output(port, b)                # ポート番号portのGPIOを出力に設定
