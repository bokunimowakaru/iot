#!/usr/bin/env python3
# coding: utf-8
# Example 13 チャイム+ボタン 【チャイム音の排他処理対応】

################################################################################
## ご注意：
## 本プログラムは Raspberry Pi 5 に対応するために、GPIO用ライブラリにGPIO Zeroを
## 使用します。
## Raspberry Pi 4 以前でも動作します。
## 書籍「Pythonで作るIoTシステム プログラム・サンプル集」のリストからの変更点は
## 変更前を各行の先頭の#で示し、変更後を各行のコメントの##で示します。
## 書籍と同じプログラムは、プログラム名に「_rpi」を付与して収録してあります。
################################################################################

port_chime = 4                                  # チャイム用 GPIO ポート番号
port_btn = 26                                   # ボタン用 GPIO ポート番号
ping_f = 554                                    # チャイム音の周波数1
pong_f = 440                                    # チャイム音の周波数2

# from RPi import GPIO                          # GPIOモジュールの取得
from gpiozero import TonalBuzzer,Button         ## TonalBuzzerとButtonを取得
from time import sleep                          # スリープ実行モジュールの取得
from sys import argv                            # 本プログラムの引数argvを取得
import threading                                # スレッド用ライブラリの取得

def chime():                                    # チャイム（スレッド用）
    mutex.acquire()                             # mutex状態に設定(排他処理開始)
    # pwm.ChangeFrequency(ping_f)               # PWM周波数の変更
    # pwm.start(50)                             # PWM出力を開始。デューティ50％
    pwm.play(ping_f)                            ## ↑
    sleep(0.5)                                  # 0.5秒の待ち時間処理
    # pwm.ChangeFrequency(pong_f)               # PWM周波数の変更
    pwm.play(pong_f)                            ## ↑
    sleep(0.5)                                  # 0.5秒の待ち時間処理
    pwm.stop()                                  # PWM出力停止
    mutex.release()                             # mutex状態の開放(排他処理終了)

print(argv[0])                                  # プログラム名を表示する
if len(argv) >= 2:                              # 引数があるとき
    port_chime = int(argv[1])                   # GPIOポート番号をport_chimeへ
if len(argv) >= 3:                              # 引数2つ以上あるとき
    port_btn = int(argv[2])                     # GPIOポート番号をport_btnへ
# GPIO.setmode(GPIO.BCM)                        # ポート番号の指定方法の設定
# GPIO.setup(port_chime, GPIO.OUT)              # ポート番号port_chimeを出力に
# GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP) # port_btn を入力に
# pwm = GPIO.PWM(port_chime, ping_f)            # PWM出力用のインスタンスを生成
pwm = TonalBuzzer(port_chime)                   ## ↑
btn = Button(port_btn)                          ## ポートport_btnをボタン入力に

mutex = threading.Lock()                        # 排他処理用のオブジェクト生成
prev = 1                                        # 前回のボタン状態を保持する

try:
    while True:                                 # 繰り返し処理
        # b = GPIO.input(port_btn)              # GPIO入力値を変数bへ代入
        b = int(not btn.value)                  ## ↑
        if prev == b:                           # 前回の値と一致
            sleep(0.1)                          # 0.1秒間の待ち時間処理
            continue                            # whileに戻る
        if b == 0:                              # ボタンが押された時
            thread = threading.Thread(target=chime) # 関数chimeをスレッド化
            thread.start()                      # スレッドchimeの起動
        print('GPIO'+str(port_btn),'=',b)       # ポート番号と変数bの値を表示
        sleep(0.1)                              # 0.1秒間の待ち時間処理
        prev = b                                # 変数prevにボタン状態を保存
except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    # GPIO.cleanup(port_chime)                  # GPIOを未使用状態に戻す
    pwm.close()                                 ## ↑
    # GPIO.cleanup(port_btn)                    # GPIOを未使用状態に戻す
    btn.close()                                 ## ↑
    exit()                                      # プログラムの終了
