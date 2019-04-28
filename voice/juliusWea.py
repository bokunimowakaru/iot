#!/usr/bin/env python3
# coding: utf-8

# Julius 天気情報
# 「今日の天気は？」「天気を調べて」で天気を回答します。
# Copyright (c) 2019 Wataru KUNINO

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import sys
import subprocess

city_id = 270000                                # 大阪の city ID=270000
                                                # 東京=130010 京都=260010
                                                # 横浜=140010 千葉=120010
                                                # 名古屋=230010 福岡=400010

julius_com = ['./juliusBase.sh|./juliusWea.py SUBPROCESS']  # Julius起動スクリプト
talk_com = ['./aquestalk.sh','']                            # AquesTalk起動スクリプト
mode = 0                                                    # 通常起動:0, 従属起動:1

argc = len(sys.argv)                                        # 引数の数をargcへ代入
print('Usage: '+sys.argv[0]+' (subpro)')                    # タイトル表示

if argc > 1:                                                # 引数があるとき
    if 'SUBPRO' in sys.argv[argc - 1].upper():              # 引数がSUBPROの時
        print('SUBPRO, this subprocess is called by a script')
        mode = 1                                            # 従属起動と判定
if mode == 0:                                               # 直接、起動した場合
    print('MAINPRO, 開始')                                  # 通常起動処理の開始表示
    print('subprocess =',julius_com[0])                     # スクリプト名を表示
    subprocess.run(julius_com,shell=True,stdin=subprocess.PIPE) # Juliusを開始する
    print('MAINPRO, 終了')                                  # 通常起動処理の終了表示
    sys.exit()                                              # プログラムを終了する

# 以下は従属起動したときの処理

def talk(text):                                             # 関数talkを定義
    talk_com[1] = '"' + text + '"'                          # メッセージを"で括る
    print('subprocess =',talk_com)                          # メッセージを表示
    subprocess.run(talk_com)                                # AquesTalk Piを起動する

def getWeather():
    url_s = 'http://weather.livedoor.com/forecast/webservice/json/v1?city='
    url_s += str(city_id)
    try:                                                    # 例外処理の監視を開始
        res = urllib.request.urlopen(url_s)                 # HTTPアクセスを実行
        res_dict = json.loads(res.read().decode())          # 受信データを変数res_dictへ代入
        res.close()                                         # HTTPアクセスの終了
        telop = res_dict['forecasts'][0]['telop']
    except Exception as e:
        print(e)                                            # エラー内容を表示
        return 'エラー'                                     # エラーを回答
    return telop                                            # 天気を回答

print('SUBPRO, 開始')                                       # 従属起動処理の開始
talk('ユリス天気情報を起動しました。')                      # 起動メッセージの出力
while mode:                                                 # modeが1の時に繰返し処理
    for line in sys.stdin:                                  # 標準入力から変数lineへ
        sp = line.find(':')                                 # 変数line内の「:」を探す
        if sp < 4 or len(line) < sp + 2:                    # その位置が条件に合わない時
            continue                                        # forループの先頭に戻る
        com = line[0:sp]                                    # 「:」までの文字列をcomへ
        if 'STAT' in com.upper() or 'PASS' in com.upper():  # 受信データがログの時
            print(line.strip())                             # ログを出力（表示）する
            continue                                        # forループの先頭に戻る
        if 'SENTENCE' in com.upper():                       # 音声認識結果の時
            voice = line[sp+1:]                             # 認識結果を変数voiceへ代入
            print('SENTENCE=',voice.strip())                # 認識結果を出力（表示）する
            if '終了' in voice:                             # 音声「終了」を認識したとき
                mode = 0                                    # 変数modeに0を代入
                break                                       # forループを抜ける
            if '天気'in voice:                              # 音声「天気」を認識したとき
                talk( '今日の天気は' + getWeather() + 'です。')
print('SUBPRO, 終了')                                       # 従属起動処理の終了表示
talk('はい終了します。さようならと言ってください。では、さようなら。')
sys.exit()
