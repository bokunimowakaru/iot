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
julius_com = ['./juliusDemo.sh']                            # Julius起動スクリプト
talk_com = ['./aquestalk.sh','']                            # AquesTalk起動スクリプト
mode = 0

argc = len(sys.argv)                                        # 引数の数をargcへ代入
print('Usage: '+sys.argv[0]+' (subpro)')                    # タイトル表示

if argc > 1:
    if 'SUBPRO' in sys.argv[argc - 1].upper():
        print('SUBPRO, this subprocess is called by a script')
        mode = 1
if mode == 0:                                               # 直接、起動した場合
    print('MAINPRO, 開始')
    print('subprocess =',julius_com[0])                     # スクリプト名を表示
    julius = subprocess.run(julius_com, shell=True)         # Juliusを開始する
    print('MAINPRO, 終了')
    sys.exit()                                              # 終了する

# 以下は juliusSpeechToUdp.sh から呼び出された時に実行する

def talk(text):
    talk_com[1] = '"' + text + '"'
    print('subprocess =',talk_com)
    subprocess.run(talk_com)

print('SUBPRO, 開始')
talk('ユリス会話デモを起動しました。')
while mode:                                                 # modeが1の時に繰返し処理
    for line in sys.stdin:                                  # 標準入力から変数lineへ
        udp = None                                          # 送信データ用変数udpを定義
        sp = line.find(':')                                 # 変数line内の「:」を探す
        if sp < 4 or len(line) < sp + 2:                    # その位置が条件に合わない時
            continue                                        # forループの先頭に戻る
        com = line[0:sp]                                    # 「:」までの文字列をcomへ
        if 'STAT' in com.upper() or 'PASS' in com.upper():  # 受信データがログの時
            print(line.strip())                             # ログを出力（表示）する
            continue                                        # forループの先頭に戻る
        if 'SENTENCE' in com.upper():                       # 音声認識結果の時
            voice = line[sp+1:].strip()                     # 認識結果を変数voiceへ代入
            print('SENTENCE=',voice)                        # 認識結果を出力（表示）する
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
print('SUBPRO, 終了')
talk('ではさようなら')
sys.exit()
