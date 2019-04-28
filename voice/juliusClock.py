#!/usr/bin/env python3
# coding: utf-8

# Julius 音声時計
# 音声「今何時？」でインターネットから時刻を取得して、回答します。
# Copyright (c) 2019 Wataru KUNINO

import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import datetime                                 # 日時変換ライブラリを組み込む
import sys
import subprocess

url_s = 'https://ntp-a1.nict.go.jp/cgi-bin/json'            # NICTアクセス先
julius_com = ['./juliusBase.sh|./juliusClock.py SUBPROCESS']# Julius起動スクリプト
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

def getNictTime():
    try:                                                    # 例外処理の監視を開始
        res = urllib.request.urlopen(url_s)                 # HTTPアクセスを実行
        res_dict = json.loads(res.read().decode())          # 受信データを変数res_dictへ代入
        res.close()                                         # HTTPアクセスの終了
        time_f = res_dict.get('st')                         # 項目stの値をtime_fへ代入
    except Exception as e:
        print(e)                                            # エラー内容を表示
        return datetime.datetime.now()                      # 内蔵時計の値を応答
    print('time_f =', time_f)                               # time_fの内容を表示
    time = datetime.datetime.fromtimestamp(time_f)          # 日時形式に変換
    print('time =', time)                                   # 日時を表示
    return time                                             # NICT時間を応答

print('SUBPRO, 開始')                                       # 従属起動処理の開始
talk('ユリス音声時計を起動しました。')                      # 起動メッセージの出力
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
            if '何 時' in voice:                            # 音声「何 時」認識時
                time = getNictTime()                        # NICTから日時を取得
                print('time =', time)                       # timeの内容を表示
                talk( str(time.hour) + '時' + str(time.minute) + '分です' )
            if '今日' in voice or '日付' in voice:          # 音声「今日」または「日付」
                time = getNictTime()                        # NICTから日時を取得
                talk( str(time.month) + '月' + str(time.day) + '日です' )
print('SUBPRO, 終了')                                       # 従属起動処理の終了表示
talk('はい終了します。さようならと言ってください。では、さようなら。')
sys.exit()
