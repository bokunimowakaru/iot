#!/usr/bin/env python3
# coding: utf-8
# Example 13' チャイム - キッチン・タイマー

port_chime = 4                                  # 圧電スピーカ用 GPIO ポート番号
port_btn = 26                                   # ボタン用 GPIO ポート番号
ping_f = 554                                    # 圧電スピーカ用 周波数1
pong_f = 440                                    # 圧電スピーカ用 周波数2
ports = [17, 27, 22, port_chime]                # 赤,緑,青色のLEDとスピーカ GPIO
colors= ['消灯','赤色','緑色','黄色','青色','赤紫色','藍緑色','白色']

from RPi import GPIO                            # GPIOモジュールの取得
from RPi time import sleep, time                # sleepとtimeモジュールの取得

def led3(color):
    if color > 0:                               # 色番号が0以上のとき
        print('Timer =', color, 'min. ',end='') # 色番号の指示値を表示
        chime(ping_f ,0.01)                     # クリック音
        if color > 7 or color < 0:              # 色番号の範囲外のとき
            color = 7                           # 白色(7)に設定
        print('Color =', color, colors[color])  # 色番号を表示
    for i in range(3):                          # LED用ポート番号を変数iへ
        port = ports[i]                         # ポート番号をportsから取得
        b = (color >> i) & 1                    # 該当LEDへの出力値を変数bへ
        GPIO.output(port, b)                    # ポート番号portのGPIOを出力に

def chime(freq ,t):
    pwm.ChangeFrequency(freq)                   # PWM周波数の変更
    pwm.start(50)                               # PWM出力を開始。デューティ50％
    sleep(t)                                    # t秒の待ち時間処理
    pwm.stop()                                  # PWM出力停止

GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
for port in ports:                              # 各ポート番号を変数portへ代入
    GPIO.setup(port, GPIO.OUT)                  # ポート番号portのGPIOを出力に
GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO 26 を入力に
pwm = GPIO.PWM(port_chime, ping_f)              # PWM出力用のインスタンスを生成

try:                                            # キー割込(Ctrl+C)の監視を開始
    while True:                                 # 繰り返し処理
        # タイマー設定
        led3(colors.index('白色'))              # LEDを白色に
        color = 0                               # 色番号0（消灯）を設定
        t = time() + 1.0                        # タイムアウト変数tを1秒後に設定
        while color == 0 or time() < t:         # 色番号が0または時間t以内のとき
            b = GPIO.input(port_btn)            # ボタン入力値を変数bへ代入
            if b == 0:                          # ボタンが押されていた時
                color += 1                      # 色番号に1を追加
                led3(color)                     # LEDを色番号で点灯
                while b == 0:                   # ボタンが押されたままのとき
                    b = GPIO.input(port_btn)    # 押されている間は待機する
                sleep(0.1)                      # チャタリング防止
                t = time() + 1.0                # タイムアウト変数tを1秒後に設定
        # タイマー開始
        t = time() + 60 * color                 # タイマー終了時間tをcolor分後に
        while time() < t:                       # タイマー終了するまで繰り返し
            led3(0)                             # LEDを消灯に
            sleep(0.5)                          # 0.5秒の待ち時間処理
            led3(int((t - time()) / 60) + 1)    # タイマー残り時間(分)
            sleep(0.5)                          # 0.5秒の待ち時間処理
        # タイマー終了
        led3(colors.index('赤紫色'))            # LEDを赤紫色に
        chime(ping_f ,0.5)                      # ブザー「Ping」音
        led3(colors.index('藍緑色'))            # LEDを藍緑色に
        chime(pong_f, 0.5)                      # ブザー「Pong」音
except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    for port in ports:                          # 各ポート番号を変数portへ代入
        GPIO.cleanup(port)                      # GPIOを未使用状態に戻す
    GPIO.cleanup(port_btn)                      # GPIOを未使用状態に戻す
