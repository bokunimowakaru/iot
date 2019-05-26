#!/usr/bin/env python3
# coding: utf-8
# Example 09 IoTセンサ用クラウド・サービスAmbientへ温度値を送信する

ambient_chid='0000'                 # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef'     # ここにはライトキーを入力
amdient_tag='d1'                    # データ番号d1～d8のいずれかを入力

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

filename='/sys/class/thermal/thermal_zone0/temp'# 温度ファイル
url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey, amdient_tag:0.0}  # 内容を変数body_dictへ

# 温度を取得する
try:                                            # 例外処理の監視を開始
    fp = open(filename)                         # 温度ファイルを開く
except Exception as e:                          # 例外処理発生時
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了
temp = float(fp.read()) / 1000                  # ファイルを読み込み1000で除算
fp.close()                                      # ファイルを閉じる
print('Temperature =',temp)                     # 温度を表示する

# Ambientへ送信
body_dict[amdient_tag] = temp
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
if len(res_str):                                # 受信テキストがあれば
    print('Response:', res_str)                 # 変数res_strの内容を表示
else:
    print('Done')                               # Doneを表示
