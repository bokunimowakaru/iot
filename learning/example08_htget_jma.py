#!/usr/bin/env python3
# coding: utf-8
# Example 08 IoT連携の基本 HTTP GET 天気情報の取得 気象庁からの取得版

# 参考文献 天気予報 API（livedoor 天気互換サービス）：
# https://weather.tsukumijima.net/
#
# 参考文献 同サービスのソースコード
# https://github.com/tsukumijima/weather-api
# https://github.com/tsukumijima/weather-api/blob/master/app/Models/Weather.php
#
#   予報情報の取得：
#   jma_api_forecast = "https://www.jma.go.jp/bosai/forecast/data/forecast/{$prefecture_id}.json";
#
#   概要テキスト(テロップ)の取得：
#   jma_api_overview = "https://www.jma.go.jp/bosai/forecast/data/overview_forecast/{$prefecture_id}.json";
#
# 【重要なご注意】
# 本ソフトウェアの利用に関して、筆者(国野 亘)は、責任を負いません。
# 気象業務法や、下記の予報業務許可に関する情報、上記参考文献の注意事項を
# 良く読んでから利用ください。
# 気象業務法   https://www.jma.go.jp/jma/kishou/info/ml-17.html
# 予報業務許可 https://www.jma.go.jp/jma/kishou/minkan/q_a_m.html

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む

city_id = 130000                                # 気象庁=130000(東京地方など)
                                                # 大阪管区気象台=270000(大阪府など)
                                                # 京都地方気象台=260000(南部など)
                                                # 横浜地方気象台=140000(東部など)
                                                # 銚子地方気象台=120000(北西部など)
                                                # 名古屋地方気象台=230000(西部など)
                                                # 福岡管区気象台=400000(福岡地方など)

url_s = 'https://www.jma.go.jp/bosai/forecast/data/forecast/'
url_s += str(city_id) + '.json'

try:                                            # 例外処理の監視を開始
    res = urllib.request.urlopen(url_s)         # HTTPアクセスを実行
    res_s = res.read().decode()                 # 受信テキストを変数res_sへ
    res.close()                                 # HTTPアクセスの終了
    res_dict = json.loads(res_s)                # 辞書型の変数res_dictへ代入
except Exception as e:
    print(e)                                    # エラー内容を表示
    exit()                                      # プログラムの終了

# 取得した情報から予報機関(気象庁、気象台)と地域名を抽出して表示する
office = res_dict[0].get('publishingOffice')    # res_dict内のpublishingOffice
timeSeries = res_dict[0].get('timeSeries')      # res_dict内のtimeSeriesを取得
areas = timeSeries[0].get('areas')              # timeSeries内のareasを取得
area = areas[0].get('area').get('name')         # areas内のarea.nameを取得
print('地域[0] =', office, area)                # officeとareaの内容を表示

# 取得した情報から天気予報を抽出して表示する（予報対象時刻と、予報内容）
weathers = areas[0].get('weathers')             # areas内のweathersを取得
for weather in weathers:
    i = weathers.index(weather)
    time = timeSeries[0]['timeDefines'][i]
    print('予報['+str(i)+'] =', time, weather)  # timeとweatherの内容を表示


'''
取得サンプル

$ ./example08_htget_jma.py
地域[0] = 気象庁 東京地方
予報[0] = 2023-01-28T11:00:00+09:00 晴れ　夕方　から　くもり
予報[1] = 2023-01-29T00:00:00+09:00 晴れ
予報[2] = 2023-01-30T00:00:00+09:00 晴れ　時々　くもり

$ curl https://www.jma.go.jp/bosai/forecast/data/overview_forecast/270000.json
{"publishingOffice":"大阪管区気象台","reportDatetime":"2023-01-28T10:32:00+09:00","targetArea":"大阪府","headlineText":"","text":"　大阪府は、強い冬型の気圧配置となっており、おおむね曇りで、雪や雨の降っている所があります。\n\n　２８日の大阪府は、強い冬型の気圧配置が続き、おおむね曇りで、夕方にかけて雪や雨の降る所がある見込みです。\n\n　２９日の大阪府は、高気圧に覆われて晴れるでしょう。\n\n　【近畿地方】\n　近畿地方は、強い冬型の気圧配置となっており、おおむね曇りで、北部を中心に雪が降っています。\n\n　２８日の近畿地方は、強い冬型の気圧配置が続き、おおむね曇りで、北部を中心に断続的に雪が降る見込みです。雷を伴う所があるでしょう。\n\n　２９日の近畿地方は、北部では寒気や湿った空気の影響でおおむね曇り、朝まで雪が降る見込みです。中部や南部では高気圧に覆われて、おおむね晴れるでしょう。明け方まで雷を伴う所がある見込みです。"}

curl https://www.jma.go.jp/bosai/forecast/data/forecast/270000.json
[{"publishingOffice":"大阪管区気象台","reportDatetime":"2023-01-28T11:00:00+09:00","timeSeries":[{"timeDefines":["2023-01-28T11:00:00+09:00","2023-01-29T00:00:00+09:00","2023-01-30T00:00:00+09:00"],"areas":[{"area":{"name":"大阪府","code":"270000"},"weatherCodes":["201","100","201"],"weathers":["くもり　時々　 晴れ　所により　夕方　まで　雪か雨","晴れ","くもり　時々　晴れ"],"winds":["西の風　やや強く　海上　では 　西の風　強く","西の風　やや強く","西の風　やや強く　後　北の風　やや強く"],"waves":["１．５メートル","１メートル","１メートル　後　１．５メートル"]}]},{"timeDefines":["2023-01-28T12:00:00+09:00","2023-01-28T18:00:00+09:00","2023-01-29T00:00:00+09:00","2023-01-29T06:00:00+09:00","2023-01-29T12:00:00+09:00","2023-01-29T18:00:00+09:00"],"areas":[{"area":{"name":"大阪府","code":"270000"},"pops":["30","10","10","10","10","10"]}]},{"timeDefines":["2023-01-28T09:00:00+09:00","2023-01-28T00:00:00+09:00","2023-01-29T00:00:00+09:00","2023-01-29T09:00:00+09:00"],"areas":[{"area":{"name":"大阪","code":"62078"},"temps":["7","7","2","8"]}]}]},{"publishingOffice":"大阪管区気象台","reportDatetime":"2023-01-28T11:00:00+09:00","timeSeries":[{"timeDefines":["2023-01-29T00:00:00+09:00","2023-01-30T00:00:00+09:00","2023-01-31T00:00:00+09:00","2023-02-01T00:00:00+09:00","2023-02-02T00:00:00+09:00","2023-02-03T00:00:00+09:00","2023-02-04T00:00:00+09:00"],"areas":[{"area":{"name":"大阪府","code":"270000"},"weatherCodes":["100","201","101","201","201","101","201"],"pops":["","30","20","30","30","20","30"],"reliabilities":["","","A","A","A","A","A"]}]},{"timeDefines":["2023-01-29T00:00:00+09:00","2023-01-30T00:00:00+09:00","2023-01-31T00:00:00+09:00","2023-02-01T00:00:00+09:00","2023-02-02T00:00:00+09:00","2023-02-03T00:00:00+09:00","2023-02-04T00:00:00+09:00"],"areas":[{"area":{"name":"大阪","code":"62078"},"tempsMin":["","2","1","2","3","1","2"],"tempsMinUpper":["","5","3","4","4","3","4"],"tempsMinLower":["","1","0","1","1","0","0"],"tempsMax":["","9","9","14","9","8","11"],"tempsMaxUpper":["","11","10","16","11","10","13"],"tempsMaxLower":["","8","7","12","8","7","8"]}]}],"tempAverage":{"areas":[{"area":{"name":"大阪","code":"62078"},"min":"2.6","max":"9.4"}]},"precipAverage":{"areas":[{"area":{"name":"大阪","code":"62078"},"min":"1.4","max":"13.3"}]}}]
'''
