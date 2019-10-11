#!/usr/bin/env python3
# coding: utf-8
# Example 36 IoT カメラ WSGI 版

# sudo apt-get install python3-picamera


from wsgiref.simple_server import make_server
import picamera
import datetime                                 # 日時・時刻用ライブラリ
import threading                                # スレッド用ライブラリの取得

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    global mutex                                # グローバル変数mutexを取得
    path  = environ.get('PATH_INFO')            # リクエスト先のパスを代入
    if path == '/cam.jpg':                      # リクエスト先がimage.jpg
        mutex.acquire()                         # mutex状態に設定(排他処理開始)
        camera.capture('cam.jpg')
        fp = open('cam.jpg', 'rb')              # 画像ファイルを開く
        res = fp.read()                         # 画像データを変数へ代入
        fp.close()                              # ファイルを閉じる
        mutex.release()                         # mutex状態の開放(排他処理終了)
        start_response(
            '200 OK',
            [('Content-type', 'image/jpeg')]
        )
    else:
        res = 'Not Found\r\n'.encode()
        start_response(
            '404 Not Found', 
            [('Content-type', 'text/plain; charset=utf-8')]
    )
    return [res]

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.rotation = 90
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
    exit()                                      # プログラムの終了
