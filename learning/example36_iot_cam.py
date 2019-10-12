#!/usr/bin/env python3
# coding: utf-8
# Example 36 IoT カメラ WSGI 版

# sudo apt-get install python3-picamera

from wsgiref.simple_server import make_server   # HTTPサーバ用ライブラリ
import picamera                                 # Piカメラ用ライブラリ
import datetime                                 # 日時・時刻用ライブラリ
import threading                                # スレッド用ライブラリの取得

def wsgi_app(environ, start_response):          # HTTPアクセス受信時の処理
    global mutex                                # グローバル変数mutexを取得
    path  = environ.get('PATH_INFO')            # リクエスト先のパスを代入
    if path == '/cam.jpg':                      # リクエスト先がcam.jpg
        mutex.acquire()                         # mutex状態に設定(排他処理開始)
        camera.capture('cam.jpg')               # Piカメラ撮影とファイル保存
        fp = open('cam.jpg', 'rb')              # 画像ファイルを開く
        res = fp.read()                         # 画像データを変数へ代入
        fp.close()                              # ファイルを閉じる
        mutex.release()                         # mutex状態の開放(排他処理終了)
        start_response('200 OK', [('Content-type', 'image/jpeg')])      # OK応答
    else:                                       # cam.jpg以外へのアクセス
        res = 'Not Found\r\n'.encode()          # 「Not Found」を応答
        start_response('404 Not Found',[('Content-type','text/plain')]) # エラー
    return [res]                                # コンテンツの応答

camera = picamera.PiCamera()                    # Piカメラのオブジェクトを生成
camera.resolution = (640, 480)                  # 撮影解像度を640x480に設定
camera.rotation = 90                            # 画像の回転角度を90度に設定
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

'''
--------------------------------------------------------------------------------
pi@raspberrypi4:~ $ wget 127.0.0.1:8080/cam.jpg
--2019-10-12 00:51:37--  http://127.0.0.1:8080/cam.jpg
127.0.0.1:8080 に接続しています... 接続しました。
HTTP による接続要求を送信しました、応答を待っています... 200 OK
長さ: 141110 (138K) [image/jpeg]
`cam.jpg' に保存中

cam.jpg 100%[===================================>] 137.80K  --.-KB/s 時間 0.002s

2019-10-12 00:51:37 (60.3 MB/s) - `cam.jpg' へ保存完了 [141110/141110]

--------------------------------------------------------------------------------
pi@raspberrypi:~ $ cd iot/learning/
pi@raspberrypi:~/iot/learning $ ./example36_iot_cam.py
HTTP port 8080
127.0.0.1 - - [12/Oct/2019 00:51:45] "GET /cam.jpg HTTP/1.1" 200 141110
192.168.0.3 - - [12/Oct/2019 00:52:36] "GET /cam.jpg HTTP/1.1" 200 130184
--------------------------------------------------------------------------------
'''
