#!/usr/bin/env python3
# coding: utf-8
# Example 25 IoT LCDへ時刻を送信する

ip = '192.168.254.1'                                # 宛先アドレスを記入

from sys import argv                                # 引数argvを取得する
import urllib.request                               # HTTP通信ライブラリ
import urllib.parse                                 # URL解析用ライブラリ
from time import sleep                              # sleepコマンドを組込
import datetime                                     # 日時処理ライブラリ

print('Usage:', argv[0], 'ip [message]')            # プログラム名と使い方
if len(argv) >= 2:                                  # 引数が存在
    ip = argv[1]                                    # 第1引数を変数ipへ
msg_flag = True                                     # トグル表示フラグ
while True:
    if len(argv) >= 3 and msg_flag:                 # 引数messageが存在
        lcd = ' '.join(argv[2:])                    # 引数を変数lcdへ
    else:
        date=datetime.datetime.today()              # 日付を取得
        lcd = date.strftime('%Y/%m/%d%H:%M:%S')     # 日付を変数lcdへ代入
        lcd = lcd[2:]                               # 3文字目以降を抽出
    url_s = 'http://' + ip + '/?DISPLAY='           # URIを作成
    url_s += urllib.parse.quote(lcd, safe='')       # URIに変数lcdを追加
    print(url_s)                                    # 作成したURLを表示
    try:
        res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
    except Exception as e:
        print(e)                                    # エラー内容を表示
        exit()                                      # プログラムの終了
    code = res.getcode()                            # HTTPリザルトを取得
    print('res =',code)                             # リザルトコードを表示
    res.close()                                     # HTTPアクセスの終了
    sleep(1)                                        # 1秒間の待ち時間処理
    msg_flag = not msg_flag                         # フラグの反転

'''
（実行例）
pi@raspberrypi:~ $ cd ~/iot/learning
pi@raspberrypi:~/iot/learning $ ./example24_rx_sens.py
Listening UDP port 1024 ...
2019/06/16 15:22, 192.168.0.8, temp0_2, 26.0
^C
KeyboardInterrupt
pi@raspberrypi:~/iot/learning $ ./example25_tx_lcd.py 192.168.0.8 This is testing
Usage: ./example25_tx_lcd.py ip [message]
http://192.168.0.8/?DISPLAY=This%20is%20testing
res = 200
http://192.168.0.8/?DISPLAY=19%2F06%2F1615%3A22%3A30
res = 200
'''
