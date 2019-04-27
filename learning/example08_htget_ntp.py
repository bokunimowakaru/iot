#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET 時刻の取得

# http://www.nict.go.jp/JST/http.html

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import datetime

url_s = 'https://ntp-a1.nict.go.jp/cgi-bin/json'# アクセス先を変数url_sへ代入

try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
except Exception as e:                          # 例外処理発生時
    print(e,url_s)                              # エラー内容と変数url_sを表示
    exit()                                      # プログラムの終了

res_s = res.read().decode()                     # 受信テキストを変数res_sへ
print('Response:', res_s)                       # 変数res_sの内容を表示

try:
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
    time_f = res_dict.get('st')                 # 項目stの値をtime_fへ代入
    print('time_f =', time_f)                   # time_fの内容を表示
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

time = datetime.datetime.fromtimestamp(time_f)  # datetime形式に変換
print('time =', time)                           # 日時を表示

print('年 =', time.year)
print('月 =', time.month)
print('日 =', time.day)
print('時 =', time.hour)
print('分 =', time.minute)
print('秒 =', time.second)
