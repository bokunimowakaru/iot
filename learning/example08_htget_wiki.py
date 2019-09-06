#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET Wikipedia情報の取得

# 参考文献：https://ja.wikipedia.org/w/api.php

from sys import argv                            # 引数argvを取得する
import urllib.request                           # HTTP通信ライブラリを組み込む
import urllib.parse
import json                                     # JSON変換ライブラリを組み込む

keyword = 'ウィキペディア'

print('Usage:', argv[0], '検索キーワード')      # プログラム名と使い方を表示

if len(argv) >= 2:                              # 引数の入力が存在した場合
    keyword = argv[1]                           # 引数の内容をkeywordへ代入

url_s = 'http://ja.wikipedia.org/w/api.php?'
url_s += 'format=json' + '&'
url_s += 'action=query' + '&'
url_s += 'prop=extracts' + '&'
url_s += 'exintro' + '&'
url_s += 'explaintext' + '&'
url_s += 'titles='
url_s += urllib.parse.quote(keyword)
print(url_s)                                    # 作成したURLを表示

try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
    res_s = res.read().decode()                 # 受信テキストを変数res_sへ
    res.close()                                 # HTTPアクセスの終了
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

# pages_dict = res_dict['query']['pages']
query_dict = res_dict.get('query')              # res_dict内のqueryを取得
pages_dict = query_dict.get('pages')            # query_dict内のpagesを取得
for pageid in pages_dict:                       # pages_dict内の全要素
    # extract = pages_dict[pageid]['extract']
    pageid_dict = pages_dict.get(pageid)        # pages_dict内の要素を取得
    extract = pageid_dict.get('extract')        # pageid_dict内のextractを取得
    if extract is None or extract == '':        # 要素または内容が無かったとき
        print('見つかりませんでした。',pageid)  # 見つかりませんでしたと表示
    else:                                       # 見つかったとき
        print(extract.split('\n')[0])           # 内容の改行までを表示
