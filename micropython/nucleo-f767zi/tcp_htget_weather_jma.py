# coding: utf-8
# IoT連携の基本 HTTP GET Weather for MicroPython
# Copyright (c) 2019-2023 Wataru KUNINO

# 参考文献 天気予報 API（livedoor 天気互換サービス）：
# https://weather.tsukumijima.net/
#
# 【重要なご注意】
# 本ソフトウェアの利用に関して、筆者(国野 亘)は、責任を負いません。
# 気象業務法や、下記の予報業務許可に関する情報、上記参考文献の注意事項を
# 良く読んでから利用ください。
# 気象業務法   https://www.jma.go.jp/jma/kishou/info/ml-17.html
# 予報業務許可 https://www.jma.go.jp/jma/kishou/minkan/q_a_m.html

import network                              # ネットワーク通信ライブラリ
import socket                               # ソケット通信ライブラリ
import json                                 # JSON変換ライブラリを組み込む
from sys import exit                        # ライブラリsysからexitを組み込む

city_id = 270000                            # 気象庁=130000(東京地方など)
                                            # 大阪管区気象台=270000(大阪府など)
                                            # 京都地方気象台=260000(南部など)
                                            # 横浜地方気象台=140000(東部など)
                                            # 銚子地方気象台=120000(北西部など)
                                            # 名古屋地方気象台=230000(西部など)
                                            # 福岡管区気象台=400000(福岡地方など)

# (停止) host_s = 'weather.livedoor.com'      # アクセス先のホスト名
# (停止) path_s = '/forecast/webservice/json/'# アクセスするパス
# (停止) path_s += 'v1?city=' + str(city_id)  # 地域を追加
# host_s = 'weather.tsukumijima.net'          # アクセス先のホスト名
# path_s = '/api/forecast/'                   # アクセスするパス
# path_s += 'city=' + str(city_id)            # 地域を追加

host_s = 'www.jma.go.jp'                    # アクセス先のホスト名
path_s = '/bosai/forecast/data/forecast/'   # アクセスするパス
path_s += str(city_id) + '.json'            # 地域を追加

pyb.LED(1).on()                             # LED(緑色)を点灯
eth = network.Ethernet()                    # Ethernetのインスタンスethを生成
try:                                        # 例外処理の監視を開始
    eth.active(True)                        # Ethernetを起動
    eth.ifconfig('dhcp')                    # DHCPクライアントを設定
except Exception as e:                      # 例外処理発生時
    print(e)                                # エラー内容を表示
    exit()

addr = socket.getaddrinfo(host_s,80)[0][-1] # ホストのIPアドレスとポートを取得
sock = socket.socket()                      # ソケットのインスタンスを生成
sock.connect(addr)                          # ホストへのTCP接続を実行
req = 'GET ' + path_s + ' HTTP/1.1\r\n'     # HTTP GET命令を文字列変数reqへ代入
req += 'Host: ' + host_s + '\r\n'           # ホスト名を追記
req += 'User-Agent: NucleoF767\r\n\r\n'     # ブラウザ名を追記
sock.send(req.encode())                     # 変数reqをバイト列に変換してTCP送信

while True:                                 # HTTPヘッダ受信の繰り返し処理
    res = sock.readline().decode()          # 1行分の受信データを変数resへ代入
    print(res.strip())                      # 改行を削除して表示
    if res == '\n' or res == '\r\n':        # ヘッダの終了を検出
        break                               # ヘッダ終了時にwhileを抜ける

body = ''                                   # 文字列変数bodyの初期化
while True:                                 # HTTPコンテンツ部の受信処理
    res = sock.readline().decode().strip()  # 1行分の受信データを変数resへ代入
    if len(res) <= 0:                       # 受信データが無い時に
        break                               # 　　　　　　　whileループを抜ける
    body += res                             # コンテンツを変数bodyへ追記

print(body)                                 # 受信コンテンツを表示
res_dict = json.loads(body)                 # JSON形式のデータを辞書型に変換
sock.close()                                # ソケットの終了
pyb.LED(1).off()                            # LED(緑色)を消灯
pyb.LED(2).off()                            # LED(青色)を消灯
pyb.LED(3).off()                            # LED(赤色)を消灯

# res_dict内の天気情報を取得
forecasts = res_dict[0]['timeSeries'][0]['areas'][0]['weathers']
i = weather.find('　')                          # 3語中1語目の終わり位置を取得
i += weather[i+1:].find('　') + 1               # 3語中2語目の終わり位置を取得
i += weather[i+1:].find('　') + 1               # 3語中3語目の終わり位置を取得
telop = weather[0:i]                            # 3語をtelopに代入
print('telop =', telop)                     # telopの内容を表示

if telop.find('晴') >= 0:
    pyb.LED(3).on()                         # LED(赤色)を点灯
if telop.find('曇') >= 0:
    pyb.LED(1).on()                         # LED(緑色)を点灯
if telop.find('雨') >= 0 or telop.find('雪') >= 0:
    pyb.LED(2).on()                         # LED(青色)を点灯
