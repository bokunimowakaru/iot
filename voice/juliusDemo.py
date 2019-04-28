#!/usr/bin/env python3
# coding: utf-8

# Julius 会話デモ
# 音声「こんにちは」で「はい、こんにちは」を、
# 音声「お元気ですか？」で「はい、元気です」を、
# 音声「あなたの名前は？」で「私の名前はJuriusです」を、
# 「アプリを終了して」で「さようなら」の会話が出来ます。
# Copyright (c) 2019 Wataru KUNINO

import sys
import subprocess
julius_com = ['./juliusBase.sh|./juliusDemo.py SUBPROCESS'] # Julius起動スクリプト
talk_com = ['./aquestalk.sh','']                            # AquesTalk起動スクリプト
mode = 0                                                    # 通常起動:0, 副次起動:1

argc = len(sys.argv)                                        # 引数の数をargcへ代入
print('Usage: '+sys.argv[0]+' (subpro)')                    # タイトル表示

if argc > 1:                                                # 引数があるとき
    if 'SUBPRO' in sys.argv[argc - 1].upper():              # 引数がSUBPROの時
        print('SUBPRO, this subprocess is called by a script')
        mode = 1                                            # 副次起動と判定
if mode == 0:                                               # 直接、起動した場合
    print('MAINPRO, 開始')                                  # 通常起動処理の開始表示
    print('subprocess =',julius_com[0])                     # スクリプト名を表示
    subprocess.run(julius_com,shell=True,stdin=subprocess.PIPE) # Juliusを開始する
    print('MAINPRO, 終了')                                  # 通常起動処理の終了表示
    sys.exit()                                              # プログラムを終了する

# 以下は副次起動したときの処理

def talk(text):                                             # 関数talkを定義
    talk_com[1] = '"' + text + '"'                          # メッセージを"で括る
    print('subprocess =',talk_com)                          # メッセージを表示
    subprocess.run(talk_com)                                # AquesTalk Piを起動する

print('SUBPRO, 開始')                                       # 副次起動処理の開始
talk('ユリス会話デモを起動しました。')                      # 起動メッセージの出力
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
            if 'こんにちは' in voice:                       # 音声「こんにちは」認識時
                talk('はいこんにちは')                      # 「はい、こんにちは」を回答
            if '元気' in voice:                             # 音声「元気」認識時
                talk('はい元気です')                        # 「はい、元気です」を回答
            if '名前' in voice:                             # 音声「元気」認識時
                talk('私の名前はユリスです')                # 「私の名前は～」を回答
            if 'さようなら' in voice or 'さよなら' in voice :
                talk('終了するときは、アプリを終了してと話してください')
print('SUBPRO, 終了')                                       # 副次起動処理の終了表示
talk('はい終了します。さようならと言ってください。では、さようなら。')
sys.exit()
