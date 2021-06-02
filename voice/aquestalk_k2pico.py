#!/usr/bin/env python3
# coding: utf-8

# AquesTalkPi に含まれる言語処理エンジン AqKanji2Koe-A を使って
# 日本語の文章を AquesTalk Pico LSI 用の音声記号列（ローマ字）に
# 変換するプログラムです。
#
# 入力した文字列を AqKanji2Koe-A に渡しすと、カタカナ表記の音声
# 記号列が得られるので、本プログラムではカタカナ部をローマ字に
# 変換します。
#
# このプログラムを実行するには、Aquest 社の AquesTalkPi が必要です。

# AquesTalk、AquesTalkPi、AqKanji2Koe、AquesTalk Pico LSIの名称や
# ソフトウェアの権利は、(株)アクエストに帰属します。

# このプログラムの権利は国野亘に帰属します。
# Copyright (c) 2021 Wataru KUNINO

import sys
import subprocess

romanV = ["a", "i", "u", "e", "o"]
romanC = ["k", "s", "t", "n", "h", "m", "y", "r", "w"]
romanN = ["nn", "-", "xtu", ",", "."]
romanCD = ["g", "z", "d", "b", "p"]
romanC2 = ["ky", "gy", "sy", "gy", "ty", "zy", "ny", "hy", "by", "py", "ts", "tw", "f", "th", "dh", "my", "ry", "sw", "zw", "dw"]

kana1 = ["ア", "イ", "ウ", "エ", "オ", 
         "カ", "キ", "ク", "ケ", "コ", 
         "サ", "シ", "ス", "セ", "ソ", 
         "タ", "チ", "ツ", "テ", "ト", 
         "ナ", "ニ", "ヌ", "ネ", "ノ", 
         "ハ", "ヒ", "フ", "ヘ", "ホ", 
         "マ", "ミ", "ム", "メ", "モ", 
         "ヤ", "×", "ユ", "×", "ヨ", 
         "ラ", "リ", "ル", "レ", "ロ",
         "ワ", "ヰ", "×", "ヱ", "ヲ"]
kanaN = ["ン", "ー", "ッ", "、", "。"]
kanaD = ["ガ", "ギ", "グ", "ゲ", "ゴ", 
         "ザ", "ジ", "ズ", "ゼ", "ゾ", 
         "ダ", "ヂ", "ヅ", "デ", "ド", 
         "バ", "ビ", "ブ", "ベ", "ボ",
         "パ", "ピ", "プ", "ペ", "ポ"]
kana2 = ["キャ","キィ","キュ","キェ","キョ",
         "ギャ","ギィ","ギュ","ギェ","ギョ",
         "シャ","シィ","シュ","シェ","ショ",
         "ジャ","ジィ","ジュ","ジェ","ジョ",
         "チャ","チィ","チュ","チェ","チョ",
         "ヂャ","ヂィ","ヂュ","ヂェ","ヂョ",
         "ニャ","ニィ","ニュ","ニェ","ニョ",
         "ヒャ","ヒィ","ヒュ","ヒェ","ヒョ",
         "ビャ","ビィ","ビュ","ビェ","ビョ",
         "ピャ","ピィ","ピュ","ピェ","ピョ",
         "ツァ","ツィ","ツゥ","ツェ","ツォ",
         "トァ","トィ","トゥ","トェ","トォ",
         "ファ","フィ","フゥ","フェ","フォ",
         "テャ","ティ","テュ","テェ","テョ",
         "デャ","ディ","デュ","デェ","デョ",
         "ミャ","ミィ","ミュ","ミェ","ミョ",
         "リャ","リィ","リュ","リェ","リョ",
         "スァ","スィ","スゥ","スェ","スォ",
         "ズァ","ズィ","ズゥ","ズェ","ズォ",
         "ドァ","ドィ","ドゥ","ドェ","ドョ"]

argc = len(sys.argv)                                        # 引数の数をargcへ代入
print('Usage: '+sys.argv[0]+' 日本語を入力')                # タイトル表示

mode = 0
talk = list()

if argc > 1:                                                # 引数があるとき
    if 'SUBPRO' in sys.argv[argc - 1].upper():              # 引数がSUBPROの時
        print('SUBPRO, this subprocess is called by a script')
        mode = 1                                            # 従属起動と判定
    else:
        for i in range(argc - 1):
            talk.append(sys.argv[i + 1])
else:
    talk.append('こんにちは')

if mode == 0:                                               # 直接、起動した場合
    for word in talk:
        aques_com = ['aquestalkpi/AquesTalkPi -t ' + word + '|./aquestalk_k2pico.py SUBPROCESS']
        print('MAINPRO, 開始')                                  # 通常起動処理の開始表示
        print('subprocess =',aques_com[0])                     # スクリプト名を表示
        subprocess.run(aques_com,shell=True,stdin=subprocess.PIPE) # Juliusを開始する
        print('MAINPRO, 終了')                                  # 通常起動処理の終了表示
    sys.exit()                                              # プログラムを終了する

else:                                                 # modeが1の時に繰返し処理
    for line in sys.stdin:                                  # 標準入力から変数lineへ
        line = line.strip()
        print(line)
        num = len(line)
        roman = ''
        for i in range(num):
            if i < num - 1:
                c = line[i:i+1]
                if c in kana2:
                    index_n = kana2.index(c)
                    Cindex = int(index_n / 5)
                    Vindex = index_n % 5
                    roman += romanC2[Cindex] + romanV[Vindex]
                    i += 1
                    continue
            c = line[i]
            if c in kana1:
                index_n = kana1.index(c)
                Cindex = int(index_n / 5)
                Vindex = index_n % 5
                if Cindex == 0:
                    roman += romanV[Vindex]
                else:
                    roman += romanC[Cindex - 1] + romanV[Vindex]
                continue
            if c in kanaN:
                index_n = kanaN.index(c)
                roman += romanN[index_n]
                continue
            if c in kanaD:
                index_n = kanaD.index(c)
                Cindex = int(index_n / 5)
                Vindex = index_n % 5
                roman += romanCD[Cindex] + romanV[Vindex]
                continue
            roman += c
        print(roman)
sys.exit()
