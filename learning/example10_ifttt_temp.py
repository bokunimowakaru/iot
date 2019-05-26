#!/usr/bin/env python3
# coding: utf-8
# Example 10 クラウド連携サービスIFTTTへトリガを送信する

ifttt_token='0123456-012345678ABCDEFGHIJKLMNOPQRSTUVWXYZ'   # ここにTokenを記入
ifttt_event='notify'                                        # イベント名を記入
message_s  ='ボタンが押されました'

from sys import argv                                # 本プログラムの引数argvを取得
from time import sleep

import urllib.request                               # HTTP通信ライブラリを組み込む
import json                                         # JSON変換ライブラリを組み込む

filename='/sys/class/thermal/thermal_zone0/temp'    # 温度ファイル
url_s = 'https://maker.ifttt.com/trigger/'+ifttt_event+'/with/key/'+ifttt_token
head_dict = {'Content-Type':'application/json'}     # 送信ヘッダを変数head_dictへ
body_dict = {'value1':''}                           # 送信内容を変数body_dictへ

while True:                                         # 永久ループ

    # 温度を取得する
    try:                                            # 例外処理の監視を開始
        fp = open(filename)                         # 温度ファイルを開く

    except Exception as e:                          # 例外処理発生時
        print(e)                                    # エラー内容を表示
        sleep(60)                                   # プログラムの一時停止(60秒)
        continue                                    # whileの先頭に戻る

    temp = float(fp.read()) / 1000                  # ファイルを読み込み1000で除算
    fp.close()                                      # ファイルを閉じる
    print('Temperature =',temp)                     # 温度を表示する

    if temp < 30:                                   # 室温が30℃未満の時
        sleep(5)                                    # プログラムの一時停止(5秒)
        continue                                    # whileの先頭に戻る
        
    # IFTTTへ送信
                                                    # アクセス先を変数url_sへ代入
    body_dict['value1'] = '室温が' + "{0:.1f}".format(temp) + '度になりました'
    print(head_dict)                                # 送信ヘッダhead_dictを表示
    print(body_dict)                                # 送信内容body_dictを表示

    post = urllib.request.Request(url_s, json.dumps(body_dict).encode(), head_dict)
                                                    # POSTリクエストデータを作成

    try:                                            # 例外処理の監視を開始
        res = urllib.request.urlopen(post)          # HTTPアクセスを実行

    except Exception as e:                          # 例外処理発生時
        print(e,url_s)                              # エラー内容と変数url_sを表示
        exit()                                      # プログラムの終了

    res_str = res.read().decode()                   # 受信テキストを変数res_strへ
    res.close()                                     # HTTPアクセスの終了
    print('Response:', res_str)                     # 変数res_strの内容を表示
    sleep(5)                                        # プログラムの一時停止(5秒)
    continue                                        # whileの先頭に戻る
