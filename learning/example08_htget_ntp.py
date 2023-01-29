#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET 時刻の取得

# NICTによるHTTPを利用した時刻配信サービスは終了しました。
# https://jjy.nict.go.jp/httphttps-index.html
#
# 技術情報
# https://jjy.nict.go.jp/QandA/reference/http-archive.html

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import datetime

'''
url_s = 'https://ntp-a1.nict.go.jp/cgi-bin/json'# アクセス先を変数url_sへ代入

try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
    res_s = res.read().decode()                 # 受信テキストを変数res_sへ
    res.close()                                 # HTTPアクセスの終了
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
    time_f = res_dict.get('st')                 # 項目stの値をtime_fへ代入
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了
print('Response:', res_s)                       # 変数res_sの内容を表示
print('time_f =', time_f)                       # time_fの内容を表示
time = datetime.datetime.fromtimestamp(time_f)  # datetime形式に変換
'''

# 代替　ここから～

# 代替実験用です。実運用は禁止します。
# アクセス回数が100回を超える場合は、スパム発信とみなして、
# プライバシーポリシーに基づいて通報いたします。
# https://bokunimo.net/blog/privacy/
res = urllib.request.urlopen('https://jjy.nict.go.jp/httphttps-index.html')
head = res.info()                               # 受信ヘッダ変数headへ
res.close()                                     # HTTPアクセスの終了
print('Response:', head)                        # 変数res_sの内容を表示
time_s = head['date']
time = datetime.datetime.strptime(time_s, '%a, %d %b %Y %H:%M:%S GMT')
print('GMT time =', time)                       # 日時を表示
time += datetime.timedelta(hours=9)
# 代替　～ここまで

print('JST time =', time)                       # 日時を表示

print('年 =', time.year)
print('月 =', time.month)
print('日 =', time.day)
print('時 =', time.hour)
print('分 =', time.minute)
print('秒 =', time.second)
