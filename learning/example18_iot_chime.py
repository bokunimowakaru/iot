#!/usr/bin/env python3
# coding: utf-8
# Example 18 IoT チャイム WSGI 版

port = 4                                        # GPIO ポート番号
ping_f = 554                                    # チャイム音の周波数1
pong_f = 440                                    # チャイム音の周波数2

from wsgiref.simple_server import make_server
# from RPi import GPIO                          # RPi内のGPIOモジュールの取得
from gpiozero import TonalBuzzer                ## GPIO Zero のTonalBuzzerを取得
from time import sleep                          # スリープ実行モジュールの取得
from sys import argv                            # 本プログラムの引数argvを取得
import threading                                # スレッド用ライブラリの取得

def chime():                                    # チャイム（スレッド用）
    global pwm                                  # グローバル変数pwmを取得
    # pwm.ChangeFrequency(ping_f)               # PWM周波数の変更
    # pwm.start(50)                             # PWM出力を開始。デューティ50％
    pwm.play(ping_f)                            ## ↑
    sleep(0.3)                                  # 0.3秒の待ち時間処理
    # pwm.ChangeFrequency(pong_f)               # PWM周波数の変更
    pwm.play(pong_f)                            ## ↑
    sleep(0.3)                                  # 0.3秒の待ち時間処理
    pwm.stop()                                  # PWM出力停止

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    thread = threading.Thread(target=chime)     # 関数chimeをスレッド化
    thread.start()                              # スレッドchimeの起動
    ok = 'OK\r\n'                               # 応答メッセージ作成
    ok = ok.encode()                            # バイト列へ変換
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [ok]                                 # 応答メッセージを返却

print(argv[0])                                  # プログラム名を表示する
if len(argv) >= 2:                              # 引数があるとき
    port = int(argv[1])                         # GPIOポート番号をportへ代入
# GPIO.setmode(GPIO.BCM)                        # ポート番号の指定方法の設定
# GPIO.setup(port, GPIO.OUT)                    # ポート番号portのGPIOを出力に
# pwm = GPIO.PWM(port, ping_f)                  # PWM出力用のインスタンスを生成
pwm = TonalBuzzer(port)                         ## ↑

try:
    httpd = make_server('', 80, wsgi_app)       # TCPポート80でHTTPサーバ実体化
    print("HTTP port 80")                       # ポート確保時にポート番号を表示
except PermissionError:                         # 例外処理発生時(アクセス拒否)
    httpd = make_server('', 8080, wsgi_app)     # ポート8080でHTTPサーバ実体化
    print("HTTP port 8080")                     # 起動ポート番号の表示
try:
    httpd.serve_forever()                       # HTTPサーバを起動
except KeyboardInterrupt:                       # キー割り込み発生時
    print('\nKeyboardInterrupt')                # キーボード割り込み表示
    # GPIO.cleanup(port)                        # GPIOを未使用状態に戻す
    pwm.close()                                 ## ↑
    exit()                                      # プログラムの終了
