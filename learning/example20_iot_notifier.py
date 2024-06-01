#!/usr/bin/env python3
# coding: utf-8
# Example 20 IoT チャイム＋フルカラーLED WSGI 版

ping_f = 554                                    # チャイム音の周波数1
pong_f = 440                                    # チャイム音の周波数2
port_R = 17                                     # 赤色LED用 GPIO ポート番号
port_G = 27                                     # 緑色LED用 GPIO ポート番号
port_B = 22                                     # 青色LED用 GPIO ポート番号
port_bell = 4                                   # ブザーのGPIO ポート番号
port_btn = 26                                   # ボタンのGPIO ポート番号

ports = [port_R, port_G, port_B]                # 各色のポート番号を配列変数へ
color = [9,9,9]                                 # 初期カラー番号の取得
# pwm = []
mutex = False

from wsgiref.simple_server import make_server   # HTTPサーバ用モジュールの取得
import socket                                   # ソケット通信ライブラリ
# from RPi import GPIO                          # GPIOモジュールの取得
from gpiozero import TonalBuzzer,Button,RGBLED  # 各種GPIOモジュールの取得
from time import sleep                          # スリープ実行モジュールの取得
import threading                                # スレッド用ライブラリの取得

def chime():                                    # チャイム（スレッド用）
    global pwm_bell                             # グローバル変数pwmを取得
    global mutex                                # グローバル変数mutexを取得
    mutex.acquire()                             # mutex状態に設定(排他処理開始)
    # pwm_bell.ChangeFrequency(ping_f)          # PWM周波数の変更
    # pwm_bell.start(50)                        # PWM出力を開始。デューティ50％
    pwm_bell.play(ping_f)                       ## ↑
    sleep(0.5)                                  # 0.5秒の待ち時間処理
    # pwm_bell.ChangeFrequency(pong_f)          # PWM周波数の変更
    pwm_bell.play(pong_f)                       ## ↑
    sleep(0.5)                                  # 0.5秒の待ち時間処理
    pwm_bell.stop()                             # PWM出力停止
    mutex.release()                             # mutex状態の開放(排他処理終了)

def chime_cb(port):                             # チャイム（スレッド用）
    thread = threading.Thread(target=chime)     # 関数chimeをスレッド化
    thread.start()                              # スレッドchimeの起動

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    path = environ.get('PATH_INFO')             # 変数pathに要求パス位置を代入
    if path == '/':                             # リクエスト先がルートのとき
        thread = threading.Thread(target=chime) # 関数chimeをスレッド化
        thread.start()                          # スレッドchimeの起動
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

def udp_app():
    global udp_run
    print('Listening UDP port', 1024, '...')                # ポート番号1024表示
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)# オプション設定
        sock.bind(('', 1024))                               # ソケットに接続
    except Exception as e:                                  # 例外処理発生時
        print(e)                                            # エラー内容を表示
        exit()                                              # プログラムの終了
    while sock and udp_run:                                 # 永遠に繰り返す
        udp = sock.recv(64).decode().strip()                # UDPパケットを取得
        if udp.isprintable():                               # 全文字が表示可能
            print('UDP :',udp)                              # 受信データを出力
            if udp.find('Ping') >= 0:                       # Pingを受信
                thread = threading.Thread(target=chime)     # 関数chime
                thread.start()                              # chimeの起動
    sock.close()

# GPIO.setmode(GPIO.BCM)                        # ポート番号の指定方法の設定
# for i in range( len(ports) ):                 # 各ポート番号のindexを変数iへ
#   GPIO.setup(ports[i], GPIO.OUT)              # ports[i]のGPIOポートを出力に
#   pwm.append( GPIO.PWM(ports[i], 1000) )      # PWM出力用のインスタンスを生成
#   pwm[i].start(0)                             # PWM出力を開始。デューティ0％
pwm = RGBLED(red=ports[0], green=ports[1], blue=ports[2]) # RGB LEDからpwmを生成

# GPIO.setup(port_bell, GPIO.OUT)               # ポートport_bellのGPIOを出力に
# pwm_bell = GPIO.PWM(port_bell, ping_f)        # PWM出力用のインスタンスを生成
pwm_bell = TonalBuzzer(port_bell)               ## ↑

# GPIO.setup(port_btn, GPIO.OUT)                # ポートport_btnのGPIOを入力に
# GPIO.setup(port_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP) # port_btnを入力に設定
# btn = GPIO.add_event_detect(port_btn, GPIO.FALLING, chime_cb, bouncetime=600)
btn = Button(port_btn, bounce_time=0.1)         ## ポート番号portをボタン入力に
btn.when_pressed = chime_cb                     # ボタン押下時にchime_cbを呼出す

udp_th = threading.Thread(target=udp_app)       # 関数udp_appをスレッド化
udp_run = True
udp_th.start()                                  # スレッドudp_thの起動
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
    # for i in range( len(ports) ):             # 各ポート番号のindexを変数iへ
    #   pwm[i].stop()                           # PWM出力停止
    #   GPIO.cleanup(ports[i])                  # LED用GPIOを未使用状態に戻す
    pwm.close()                                 ## ↑
    # GPIO.cleanup(port_bell)                   # チャイム用GPIOを未使用状態に
    pwm_bell.close()                            ## ↑
    # GPIO.cleanup(port_btn)                    # ボタン用GPIOを未使用状態に戻す
    btn.close()                                 ## ↑
    exit()                                      # プログラムの終了
