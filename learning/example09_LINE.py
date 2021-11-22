#!/usr/bin/env python3
# coding: utf-8
# Example 09 LINEへ温度値を送信する

'''
 ※LINE アカウントと LINE Notify 用のトークンが必要です。
    1. https://notify-bot.line.me/ へアクセス
    2. 右上のアカウントメニューから「マイページ」を選択
    3. アクセストークンの発行で「トークンを発行する」を選択
    4. トークン名「raspi」（任意）を入力
    5. 送信先のトークルームを選択する（「1:1でLINE Notifyから通知を受け取る」など）
    6. [発行する]ボタンでトークンが発行される
    7. [コピー]ボタンでクリップボードへコピー
    8. 下記のline_tokenに貼り付け
'''

line_token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
                                                # ↑ここにLINEで取得したTOKENを入力

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

filename='/sys/class/thermal/thermal_zone0/temp'# 温度ファイル
url_s = 'https://notify-api.line.me/api/notify' # アクセス先
head_dict = {'Authorization':'Bearer ' + line_token,
             'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
                                                # ヘッダを変数head_dictへ

# 温度を取得する
try:                                            # 例外処理の監視を開始
    fp = open(filename)                         # 温度ファイルを開く
except Exception as e:                          # 例外処理発生時
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了
temp = float(fp.read()) / 1000                  # ファイルを読み込み1000で除算
fp.close()                                      # ファイルを閉じる
print('Temperature =',temp)                     # 温度を表示する

# LINEへ送信
body = 'message=温度の測定値は ' + '{:.1f}'.format(temp) + '℃ です。'
                                                # 送信メッセージ
print(head_dict)                                # 送信ヘッダhead_dictを表示
print(body)                                     # 送信内容bodyを表示
post = urllib.request.Request(url_s, body.encode(), head_dict)
                                                # POSTリクエストデータを作成
try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(post)          # HTTPアクセスを実行
except Exception as e:                          # 例外処理発生時
    print(e,url_s)                              # エラー内容と変数url_sを表示
    exit()                                      # プログラムの終了
res_str = res.read().decode()                   # 受信テキストを変数res_strへ
res.close()                                     # HTTPアクセスの終了
if len(res_str):                                # 受信テキストがあれば
    print('Response:', res_str)                 # 変数res_strの内容を表示
else:
    print('Done')                               # Doneを表示
