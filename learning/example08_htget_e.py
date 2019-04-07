#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET 【例外処理対応版】

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

url = 'https://bokunimo.net/iot/cq/test.json'   # HTTPアクセス先を変数urlへ代入

try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(url)           # HTTPアクセスを実行
except Exception as e:                          # 例外処理発生時
    print(e,url)                                # エラー内容と変数urlを表示
    exit()                                      # プログラムの終了

res_str = res.read().decode()                   # 受信テキストを変数res_strへ
print('Response:', res_str)                     # 変数res_strの内容を表示

try:
    res_dict = json.loads(res_str)              # 辞書型の変数res_dictへ代入
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

print('title :', res_dict.get('title'))         # 項目'title'の内容を取得・表示
print('descr :', res_dict.get('descr'))         # 項目'descr'の内容を取得・表示
print('state :', res_dict.get('state'))         # 項目'state'の内容を取得・表示
print('url   :', res_dict.get('url'))           # 項目'url'内容を取得・表示
print('date  :', res_dict.get('date'))          # 項目'date'内容を取得・表示
