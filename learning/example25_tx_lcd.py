#!/usr/bin/env python3
# coding: utf-8
# Example 25 IoT LCDへ時刻を送信する

ip = '192.168.254.1'                            # 宛先アドレスを記入

from sys import argv                            # 引数argvを取得する
import urllib.request                           # HTTP通信ライブラリ
import urllib.parse
import datetime

if len(argv) >= 2:                              # 引数の入力が存在
    lcd = argv[1]                               # 引数を変数lcdへ
else:
    date=datetime.datetime.today()              # 日付を取得
    lcd = date.strftime('%Y/%m/%d%H:%M:%S')     # 日付を変数lcdへ代入
    lcd = lcd[2:]                               # 3文字目以降を抽出
url_s = 'http://' + ip + '/?DISPLAY='           # URIを作成
url_s += urllib.parse.quote(lcd)                # URIに変数lcdを追加
print(url_s)                                    # 作成したURLを表示

try:
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了
code = res.getcode()                            # HTTPリザルトを取得
print('code =',code)                            # コードを表示
res.close()                                     # HTTPアクセスの終了
