#!/usr/bin/env python3
# coding: utf-8
# Example 19 IoT フルカラーLED WSGI 版

################################################################################
## ご注意：
## 本プログラムは Raspberry Pi 5 に対応するために、GPIO用ライブラリにGPIO Zeroを
## 使用します。
## Raspberry Pi 4 以前でも動作します。
## 書籍「Pythonで作るIoTシステム プログラム・サンプル集」のリストからの変更点は
## 変更前を各行の先頭の#で示し、変更後を各行のコメントの##で示します。
## 書籍と同じプログラムは、プログラム名に「_rpi」を付与して収録してあります。
################################################################################

port_R = 17                                     # 赤色LED用 GPIO ポート番号
port_G = 27                                     # 緑色LED用 GPIO ポート番号
port_B = 22                                     # 青色LED用 GPIO ポート番号

ports = [port_R, port_G, port_B]                # 各色のポート番号を配列変数へ
color = [9,9,9]                                 # 初期カラー番号の取得
# pwm = []

from wsgiref.simple_server import make_server   # HTTPサーバ用モジュールの取得
# from RPi import GPIO                          # GPIOモジュールの取得
from gpiozero import RGBLED                     # RGB LEDモジュールの取得

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    global pwm                                  # グローバル変数pwmを取得
    global color                                # グローバル変数colorの取得
    # color = [9,9,9]                           # 白色を代入
    query = environ.get('QUERY_STRING')         # 変数queryにHTTPクエリを代入
    keys = ['R=','G=','B=']                     # Query内の検索キーをkeysへ代入
    for i in range( len(keys) ):                # 検索キーのindexを変数iへ
        sp = query.upper().find(keys[i])        # 変数query内を検索する
        if sp >= 0 and sp + 2 < len(query):     # 発見位置が有効範囲内
            if query[sp+2].isdigit():           # 取得値が1桁の数値の時
                color[i] = int( query[sp+2] )   # 取得値(数値)を変数colorへ
                color[i] %= 10                  # 輝度数(10段階)の0～9に正規化
    print('Color =',color)                      # 配列変数colorの内容を表示
    w = list()                                  ## パルス幅のリストを定義
    for i in range( len(ports) ):               # 各ポート番号のindexを変数iへ
        port = ports[i]                         # ポート番号をportsから取得
        if color[i] > 0:                        # 輝度が0以外の時
            # w = int(10 ** (color[i] / 4.5))   # パルス幅wを設定(1～9⇒1～100)
            w.append(int(10 ** (color[i] / 4.5))) ## ↑
        else:                                   # 輝度が0の時
            # w = 0                             # パルス幅を0％へ
            w.append = 0                        ## ↑
        # print('GPIO'+str(port),'=',w)         # ポート番号と変数wの値を表示
        print('GPIO'+str(port),'=',w[i])        ## ↑
        # pwm[i].ChangeDutyCycle(w)
        w[i] = w[i] / 100                       ## RGBLED用に範囲調整(0.0～1.0)
        if w[i] > 1:                            ## パルス幅が1.0を超えるとき
            w[i] = 1.0                          ## RGBLEDの最大値は1.0
    pwm.color = w                               ## RGBLEDにパルス幅を設定
    ok = 'Color=' + str(color) + '\r\n'         # 応答文を作成
    ok = ok.encode('utf-8')                     # バイト列へ変換
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [ok]                                 # 応答メッセージを返却

# GPIO.setmode(GPIO.BCM)                        # ポート番号の指定方法の設定
# for i in range( len(ports) ):                 # 各ポート番号のindexを変数iへ
#   GPIO.setup(ports[i], GPIO.OUT)              # ports[i]のGPIOポートを出力に
#   pwm.append( GPIO.PWM(ports[i], 1000) )      # PWM出力用のインスタンスを生成
#   pwm[i].start(0)                             # PWM出力を開始。デューティ0％
pwm = RGBLED(red=ports[0], green=ports[1], blue=ports[2]) # RGB LEDからpwmを生成

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
    # for i in range( len(ports) ):             # 各ポート番号のindexを変数iへ
    #   pwm[i].stop()                           # PWM出力停止
    #   GPIO.cleanup(ports[i])                  # GPIOを未使用状態に戻す
    pwm.close()                                 ## ↑
    exit()                                      # プログラムの終了
