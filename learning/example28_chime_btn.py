#!/usr/bin/env python3
# coding: utf-8

################################################################################
## ご注意：
## 本プログラムは Raspberry Pi 5 に対応するために、GPIO用ライブラリにGPIO Zeroを
## 使用します。
## Raspberry Pi 4 以前でも動作します。
## 書籍「Pythonで作るIoTシステム プログラム・サンプル集」のリストからの変更点は
## 変更前を各行の先頭の#で示し、変更後を各行のコメントの##で示します。
## 書籍と同じプログラムは、プログラム名に「_rpi」を付与して収録してあります。
################################################################################

# Example 28 IoTボタンでチャイム音・玄関呼び鈴システム
# IoTボタンが送信するUDPを受信し、チャイム音を鳴り分ける

# 接続図
#           [IoTボタン] ------> [本機]
#           ボタン操作          チャイム音

# 機器構成
#   本機        GPIOポート4にブザー
#   IoTボタン   example14_iot_btn.py

port = 4                                        # GPIO ポート番号
ping_f = 554                                    # チャイム音の周波数1
pong_f = 440                                    # チャイム音の周波数2

import socket                                   # IP通信用モジュールの組み込み
# from RPi import GPIO                          # RPi内のGPIOモジュールの取得
from gpiozero import TonalBuzzer                ## GPIO Zero のTonalBuzzerを取得
from time import sleep                          # スリープ実行モジュールの取得
import threading                                # スレッド用ライブラリの取得

def chime(key):                                 # チャイム（スレッド用）
    global pwm                                  # グローバル変数pwmを取得
    if key == "Ping":
        # pwm.ChangeFrequency(ping_f)           # PWM周波数の変更
        # pwm.start(50)                         # PWM出力を開始。50％
        pwm.play(ping_f)                        ## ↑
        sleep(1)                                # 1秒の待ち時間処理
        pwm.stop()                              # PWM出力停止
    if key == "Pong":
        # pwm.ChangeFrequency(pong_f)           # PWM周波数の変更
        # pwm.start(50)                         # PWM出力を開始。50％
        pwm.play(pong_f)                        ## ↑
        sleep(0.3)                              # 0.3秒の待ち時間処理
        pwm.stop()                              # PWM出力停止

# GPIO.setmode(GPIO.BCM)                        # ポート番号の指定方法の設定
# GPIO.setup(port, GPIO.OUT)                    # ポート番号portのGPIOを出力に
# pwm = GPIO.PWM(port, ping_f)                  # PWM出力用のインスタンスを生成
pwm = TonalBuzzer(port)                         ## ↑

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while sock:                                             # 永遠に繰り返す
    try:
        udp, udp_from = sock.recvfrom(64)               # UDPパケットを取得
    except KeyboardInterrupt:                           # キー割り込み発生時
        print('\nKeyboardInterrupt')                    # キーボード割り込み表示
        # GPIO.cleanup(port)                            # GPIOを未使用状態に戻す
        pwm.close()                                     ## ↑
        exit()                                          # プログラムの終了
    udp = udp.decode().strip()                          # データを文字列へ変換
    if not udp.isprintable() or len(udp) != 4:          # 4文字以下で表示可能
        continue
    print('device =', udp, udp_from[0])                 # 取得値を表示
    if udp == 'Ping':                                   # 「Ping」に一致する時
        thread = threading.Thread(target=chime, args=([udp]))   # スレッド生成
        thread.start()                                  # スレッドchimeの起動
    if udp == 'Pong':                                   # 「Pong」に一致する時
        thread = threading.Thread(target=chime, args=([udp]))   # スレッド生成
        thread.start()                                  # スレッドchimeの起動
