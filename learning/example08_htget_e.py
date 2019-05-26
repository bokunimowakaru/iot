#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET 【例外処理対応版】

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

url_s = 'https://bokunimo.net/iot/cq/test.json' # アクセス先を変数url_sへ代入

try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
except Exception as e:                          # 例外処理発生時
    print(e,url_s)                              # エラー内容と変数url_sを表示
    exit()                                      # プログラムの終了

res_s = res.read().decode()                     # 受信テキストを変数res_sへ
res.close()                                     # HTTPアクセスの終了
print('Response:', res_s)                       # 変数res_sの内容を表示

try:                                            # 例外処理の監視を開始
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
except Exception as e:                          # 例外処理発生時
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

print('title :', res_dict.get('title'))         # 項目'title'の内容を取得・表示
print('descr :', res_dict.get('descr'))         # 項目'descr'の内容を取得・表示
print('state :', res_dict.get('state'))         # 項目'state'の内容を取得・表示
print('url   :', res_dict.get('url'))           # 項目'url'内容を取得・表示
print('date  :', res_dict.get('date'))          # 項目'date'内容を取得・表示
