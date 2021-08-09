#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET 天気情報の取得

# 参考文献
#
# ・livedoor 天気（サービス終了）：
# 	http://weather.livedoor.com/weather_hacks/webservice
#
# ・天気予報 API（livedoor 天気互換）：
# 	https://weather.tsukumijima.net/

# ご注意
# livedoor 天気 のサービス終了に伴い、互換サービスを利用します。
# 参考文献「天気予報 API（livedoor 天気互換）」の注意事項などをよく読んで
# ください。
# これらのサービスの利用に関して、何らかの損失が生じたとしても、
# 筆者(国野 亘)は、一切の責任を負いません。

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
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
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

