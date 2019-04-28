#!/usr/bin/env python3
# coding: utf-8

# Julius 百科事典
# 「インターネットで●●を調べて」でWikipediaから情報を取得して、回答します。
# 「インターネットで『パイソン』の意味を調べて」
# Copyright (c) 2019 Wataru KUNINO

import urllib.request                           # HTTP通信ライブラリを組み込む
import urllib.parse
import json                                     # JSON変換ライブラリを組み込む
import datetime                                 # 日時変換ライブラリを組み込む
import sys
import subprocess

url_s = 'https://ntp-a1.nict.go.jp/cgi-bin/json'            # NICTアクセス先
julius_com = ['./juliusBase.sh|./juliusWikip.py SUBPROCESS']# Julius起動スクリプト
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

def getKnowledge(keyword):
    url_s = 'http://ja.wikipedia.org/w/api.php?'
    url_s += 'format=json' + '&'
    url_s += 'action=query' + '&'
    url_s += 'prop=extracts' + '&'
    url_s += 'exintro' + '&'
    url_s += 'explaintext' + '&'
    url_s += 'titles='
    url_s += urllib.parse.quote(keyword)
    try:                                                    # 例外処理の監視を開始
        res = urllib.request.urlopen(url_s)                 # HTTPアクセスを実行
        res_dict = json.loads(res.read().decode())          # 受信データを変数res_dictへ代入
        res.close()                                         # HTTPアクセスの終了
        pages_dict = res_dict['query']['pages']
        pageid = list(pages_dict.keys())
        extract = pages_dict[pageid[0]]['extract']
    except Exception as e:
        print(e)                                            # エラー内容を表示
        return 'エラー'                                     # エラーを回答
    if extract != '':                                       # 内容が空で無い時
        return extract                                      # 内容を回答
    return '不明'                                           # NICT時間を応答

print('SUBPRO, 開始')                                       # 従属起動処理の開始
talk('ユリス百科事典を起動しました。')                      # 起動メッセージの出力
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
            if 'ネット で 'in voice:                        # 音声「ネットで…」
                ep = 0
                sp = voice.find('ネット で ')
                if ' を 調べ'in voice:
                    ep = voice.find(' を 調べ')
                if ' を 検索'in voice:
                    ep = voice.find(' を 検索')
                if ep > 0:
                    if ' の 意味 ' in voice:
                        ep = voice.find(' の 意味 ')
                    if sp < 0 or ep <= sp:
                        break
                    else:
                        words_list = voice[sp+6:ep].split(" ")
                        keyword = ''
                        for word in words_list:
                            if len(word) > 1:
                                keyword += word
                        talk( keyword + 'の意味は' + getKnowledge(keyword) + 'です。')
print('SUBPRO, 終了')                                       # 従属起動処理の終了表示
talk('はい終了します。さようならと言ってください。では、さようなら。')
sys.exit()
