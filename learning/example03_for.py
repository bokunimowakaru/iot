#!/usr/bin/env python3
# coding: utf-8
# Example 03 コンピュータお得意の繰り返しfor文

from sys import argv                    # 本プログラムの引数argvを取得する

for name in argv:                       # 引数を変数nameへ代入
    print('Hello,', name + '!')         # 変数nameの内容を、文字列Helloに続いて表示

# for文の「argv」を「argv[1:]」にするとargv[1]以降の全引数を順次nameへ代入して繰り返す
