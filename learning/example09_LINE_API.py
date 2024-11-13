#!/usr/bin/env python3
# coding: utf-8
# Example 09 LINEへ温度値を送信する 【 Messaging API版 】

###############################################################################
#
# LINE 公式アカウントと Messaging API 用のChannel情報が必要です。
#   1. https://entry.line.biz/start/jp/ からLINE公式アカウントを取得する
#   2. https://manager.line.biz/ の設定で「Messaging APIを利用する」を実行する
#   3. Channel 情報 (Channel ID と Channel secret) を取得する
#   4. スクリプト内の変数 line_ch_id にChannel IDを記入する
#   5. スクリプト内の変数 line_ch_pw にChannel secretを記入する
#
#                      Copyright (c) 2024 Wataru KUNINO (https://bokunimo.net/)
###############################################################################
# 注意事項
# ・メッセージ送信回数の無料枠は200回/月です。超過分は有料となります。
# ・15分間だけ有効なステートレスチャネルアクセストークンを使用しています。
# 　本スクリプトでは、実行の度にTokenを取得するので問題ありません。
# 　関数line_notifyを複数回、呼び出すような場合は、15分以内にget_line_tokenで
# 　Tokenを再取得してください。(このスクリプトを改変する場合)
###############################################################################

# Messaging API用 Channel情報
line_ch_id="0000000000"                         # LINEで取得した Channel ID
line_ch_pw="00000000000000000000000000000000"   # LINEで取得した Channel secret
url_s="https://api.line.me/"                    # LINE Messaging API のURL
url_token_s = url_s + "oauth2/v3/token"         # Token取得用のURL
url_broad_s = url_s + "v2/bot/message/broadcast" # MessageのBroadcast送信用URL

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

def get_line_token():
    head_dict = {'Content-Type':'application/x-www-form-urlencoded'}
    body =  'grant_type=client_credentials&'
    body += 'client_id=' + line_ch_id + '&'
    body += 'client_secret=' + line_ch_pw
    post = urllib.request.Request(url_token_s,body.encode(),head_dict)
    try:                                            # 例外処理の監視を開始
        res = urllib.request.urlopen(post)          # HTTPアクセスを実行
        res_s = res.read().decode()                 # 受信テキストを変数res_sへ
        res.close()                                 # HTTPアクセスの終了
        res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
    except Exception as e:                          # 例外処理発生時
        print(e,url_s)                              # エラー内容と変数url_sを表示
        exit()                                      # プログラムの終了
    return res_dict

# LINE Token (ステートレスチャネルアクセストークン) を取得する
line_token = get_line_token().get('access_token')

# 温度を取得する
filename='/sys/class/thermal/thermal_zone0/temp'# 温度ファイル
try:                                            # 例外処理の監視を開始
    fp = open(filename)                         # 温度ファイルを開く
except Exception as e:                          # 例外処理発生時
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了
temp = float(fp.read()) / 1000                  # ファイルを読み込み1000で除算
fp.close()                                      # ファイルを閉じる
print('Temperature =',temp)                     # 温度を表示する

# LINEへ送信する
head_dict = {'Authorization':'Bearer ' + line_token,
             'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body = '温度の測定値は ' + '{:.1f}'.format(temp) + '℃ です。' # 送信メッセージ
body_json='{"messages":[{"type":"text","text":"' + body + '"}]}'
print(head_dict)                                # 送信ヘッダhead_dictを表示
print(body)                                     # 送信内容bodyを表示
post = urllib.request.Request(url_broad_s, body_json.encode(), head_dict)
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

###############################################################################
# 参考文献：下記のcurl文の一部を引用しました
# LINE DevelopersLINE Developers, Messaging APIリファレンス
# https://developers.line.biz/ja/reference/messaging-api/
###############################################################################
