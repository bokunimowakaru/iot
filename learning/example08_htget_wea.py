#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET 天気情報の取得

# 参考文献 天気予報 API（livedoor 天気互換サービス）：
# https://weather.tsukumijima.net/
#
# 【重要なご注意】
# livedoor 天気 のサービス終了に伴い、上記の互換サービスを利用します。
# 同サービスは、気象庁による気象予報をlivedoor天気の互換形式に変換して配信します。
# (2023年1月28日現在、気象予報そのものは行っていない)
# 同サービスや本ソフトウェアの利用に関して、筆者(国野 亘)は、責任を負いません。
# 気象業務法や、下記の予報業務許可に関する情報、上記参考文献の注意事項を
# 良く読んでから利用ください。
# 気象業務法   https://www.jma.go.jp/jma/kishou/info/ml-17.html
# 予報業務許可 https://www.jma.go.jp/jma/kishou/minkan/q_a_m.html
#
# なお、気象庁の気象予報情報を取得する example08_htget_jma.py も用意しました。

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

city_id = 270000                                # 大阪の city ID=270000
                                                # 東京=130010 京都=260010
                                                # 横浜=140010 千葉=120010
                                                # 名古屋=230010 福岡=400010

# url_s = 'http://weather.livedoor.com/forecast/webservice/json/v1?city='
url_s = 'https://weather.tsukumijima.net/api/forecast?city='
url_s += str(city_id)

try:                                            # 例外処理の監視を開始
    req = urllib.request.Request(url_s, headers={"User-Agent": "htget_wea"})
    res = urllib.request.urlopen(req)           # HTTPアクセスを実行
    res_s = res.read().decode()                 # 受信テキストを変数res_sへ
    res.close()                                 # HTTPアクセスの終了
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

location = res_dict.get('location')             # res_dict内のlocationを取得
pref = location.get('prefecture')               # location内のprefectureを取得
city = location.get('city')                     # location内のcityを取得
print('city =', pref, city)                     # prefとcityの内容を表示

# print('telop =', res_dict['forecasts'][0]['telop'])
forecasts = res_dict.get('forecasts')           # res_dict内のforecastsを取得
telop = forecasts[0].get('telop')               # forecasts内のtelopを取得
print('telop =', telop)                         # telopの内容を表示

# print('text =', res_dict['description']['text'].split('\n')[0].strip())
description = res_dict.get('description')       # res_dict内のdescriptionを取得
text = description.get('text')                  # description内のtextを取得
text = text.split('\n')[0].strip()              # textの先頭行を抽出
print('text =', text)                           # textの内容を表示

