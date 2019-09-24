#!/usr/bin/env python3
# coding: utf-8

################################################################################
# web_serv WSGI 版
#
#                                               Copyright (c) 2019 Wataru KUNINO
################################################################################

from wsgiref.simple_server import make_server
Res_Html = [('Content-type', 'text/html; charset=utf-8')]
Res_Text = [('Content-type', 'text/plain; charset=utf-8')]
Res_Png  = [('Content-type', 'image/png')]

def wsgi_app(environ, start_response):              # HTTPアクセス受信時の処理
    path  = environ.get('PATH_INFO')                # リクエスト先のパスを代入
    query = environ.get('QUERY_STRING')             # クエリを代入

    res = None                                      # 応答値を代入する変数の定義

    if path == '/ok.txt':                           # リクエスト先がok.txtの時
        res = 'OK\r\n'.encode()                     # 応答メッセージ作成
        start_response('200 OK', Res_Text)          # TXT形式での応答を設定

    if path == '/ok.html':                          # リクエスト先がok.htmlの時
        res = '<html><h3>OK</h3></html>'.encode()   # 応答メッセージ作成
        start_response('200 OK', Res_Html)          # HTML形式での応答を設定

    if path == '/image.png':                        # リクエスト先がimage.png
        fp = open('html/image.png', 'rb')           # 画像ファイルを開く
        res = fp.read()                             # 画像データを変数へ代入
        fp.close()                                  # ファイルを閉じる
        start_response('200 OK', Res_Png)           # PNG形式での応答を設定

    if path == '/' or path[0:7] == '/index.':       # リクエスト先がルート
        fp = open('html/index.html', 'r')           # HTMLファイルを開く
        res = fp.read().encode()                    # HTML本文を変数へ代入
        fp.close()                                  # ファイルを閉じる
        start_response('200 OK', Res_Html)          # TXT形式での応答を設定

    if res is not None:                             # 変数res
        return [res]                                # 応答メッセージを返却
    else:
        res = 'Not Found\r\n'.encode()
        start_response('404 Not Found', Res_Text)
        return [res]                                # 応答メッセージを返却

try:
    httpd = make_server('', 80, wsgi_app)           # ポート80でHTTPサーバ実体化
    print("HTTP port 80")                           # 成功時にポート番号を表示
except PermissionError:                             # 例外処理発生時に
    httpd = make_server('', 8080, wsgi_app)         # ポート8080でサーバ実体化
    print("HTTP port 8080")                         # 起動ポート番号の表示
httpd.serve_forever()                               # HTTPサーバを起動
