#!/usr/bin/env python3
# coding: utf-8
# Example 18 IoT チャイム WSGI 版 【複数種のチャイム音対応版】

port = 4                                        # GPIO ポート番号
ping_f = 554                                    # チャイム音の周波数1
pong_f = 440                                    # チャイム音の周波数2
pingAlt_f = 587                                 # 警告音の周波数1
pongAlt_f = 699                                 # 警告音の周波数2

from wsgiref.simple_server import make_server
from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # スリープ実行モジュールの取得
from sys import argv                            # 本プログラムの引数argvを取得
import threading                                # スレッド用ライブラリの取得

def chime(level):                               # チャイム（スレッド用）
    if level is None or level <= 0 or level > 3:    # 範囲外の値の時に
        mutex.acquire()                         # mutex状態に設定(排他処理開始)
        pwm.ChangeFrequency(ping_f)             # PWM周波数の変更
        pwm.start(50)                           # PWM出力を開始。デューティ50％
        sleep(0.5)                              # 0.5秒の待ち時間処理
        pwm.ChangeFrequency(pong_f)             # PWM周波数の変更
        sleep(0.5)                              # 0.5秒の待ち時間処理
        pwm.stop()                              # PWM出力停止
        mutex.release()                         # mutex状態の開放(排他処理終了)
        return                                  # 戻る
    if level >= 1:                              # 警告レベル1以上のとき
        mutex.acquire()                         # mutex状態に設定(排他処理開始)
        pwm.ChangeFrequency(pingAlt_f)          # PWM周波数の変更
        pwm.start(50)                           # PWM出力を開始。50％
        sleep(0.1)                              # 0.1秒の待ち時間処理
        pwm.stop()                              # PWM出力停止取得
        mutex.release()                         # mutex状態の開放(排他処理終了)
    if level >= 2:                              # 警告レベル2以上のとき
        mutex.acquire()                         # mutex状態に設定(排他処理開始)
        pwm.ChangeFrequency(pongAlt_f)          # PWM周波数の変更
        pwm.start(50)                           # PWM出力を開始。50％
        sleep(0.2)                              # 0.2秒の待ち時間処理
        pwm.stop()                              # PWM出力停止
        mutex.release()                         # mutex状態の開放(排他処理終了)
    if level >= 3:                              # 警告レベル3のとき
        for i in range(23):                     # 下記を23回繰り返す
            sleep(0.1)                          # 0.1秒の待ち時間処理
            chime(2)                            # レベル2と同じ鳴音処理

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    level = 0
    query = environ.get('QUERY_STRING')         # 変数queryにHTTPクエリを代入
    sp = query.find('=')                        # 変数query内の「=」を探す
    if sp >= 0 and sp + 1 < len(query):         # 「=」の発見位置が有効範囲内
        if query[sp+1:].isdigit():              # 取得値が数値の時
            level = int( query[sp+1:] )         # 取得値(数値)を変数colorへ
            level %= 4                          # levelは1～3
    print('level =',level)                      # level番号を表示
    ok = 'Level=' + str(level) + '\r\n'         # 応答文を作成
    ok = ok.encode('utf-8')                     # バイト列へ変換
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    if environ['PATH_INFO'] == '/':             # リクエスト先がルートのとき
        thread = threading.Thread(target=chime, args=([level])) # 関数chime
        thread.start()                          # スレッドchimeの起動
    return [ok]                                 # 応答メッセージを返却

print(argv[0])                                  # プログラム名を表示する
if len(argv) >= 2:                              # 引数があるとき
    port = int(argv[1])                         # GPIOポート番号をportへ代入
GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポート番号portのGPIOを出力に
pwm = GPIO.PWM(port, ping_f)                    # PWM出力用のインスタンスを生成
mutex = threading.Lock()                        # 排他処理用のオブジェクト生成

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
    GPIO.cleanup(port)                          # GPIOを未使用状態に戻す
    exit()                                      # プログラムの終了
