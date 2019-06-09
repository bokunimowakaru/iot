#!/usr/bin/env python3
# coding: utf-8
# Example 17 IoT カラーLED WSGI 版

port_R = 17                                     # 赤色LED用 GPIO ポート番号
port_G = 27                                     # 緑色LED用 GPIO ポート番号
port_B = 22                                     # 青色LED用 GPIO ポート番号

ports = [port_R, port_G, port_B]                # 各色のポート番号を配列変数へ
colors= ['消灯','赤色','緑色','黄色','青色','赤紫色','藍緑色','白色']
color = colors.index('白色')                    # 初期カラー番号の取得（白色=7）

from wsgiref.simple_server import make_server   # HTTPサーバ用モジュールの取得
from RPi import GPIO                            # GPIOモジュールの取得

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    global color                                # グローバル変数colorの取得
    color = colors.index('白色')                # 白色を代入
    query = environ.get('QUERY_STRING')         # 変数queryにHTTPクエリを代入
    sp = query.find('=')                        # 変数query内の「=」を探す
    if sp >= 0 and sp + 1 < len(query):         # 「=」の発見位置が有効範囲内
        if query[sp+1:].isdigit():              # 取得値が数値の時
            color = int( query[sp+1:] )         # 取得値(数値)を変数colorへ
            color %= len(colors)                # 色数(8色)に対してcolorは0～7
    print('Color =',color,colors[color])        # 色番号と色名を表示
    for i in range( len(ports) ):               # 各ポート番号のindexを変数iへ
        port = ports[i]                         # ポート番号をportsから取得
        b = (color & ( 1 << i) ) >> i           # 該当LEDへの出力値を変数bへ
        print('GPIO'+str(port),'=',b)           # ポート番号と変数bの値を表示
        GPIO.output(port, b)                    # ポート番号portのGPIOを出力に
    ok = 'Color=' + str(color) + ' (' + colors[color] + ')\r\n' # 応答文を作成
    ok = ok.encode('utf-8')                     # バイト列へ変換
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [ok]                                 # 応答メッセージを返却

GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
for port in ports:                              # 各ポート番号を変数portへ代入
    GPIO.setup(port, GPIO.OUT)                  # ポート番号portのGPIOを出力に

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
    for port in ports:                          # 各ポート番号を変数portへ代入
        GPIO.cleanup(port)                      # GPIOを未使用状態に戻す
    exit()                                      # プログラムの終了
