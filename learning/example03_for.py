#!/usr/bin/env python3
# coding: utf-8
# Example 03 コンピュータお得意の繰り返しfor文

from sys import argv                    # 本プログラムの引数argvを取得する

print(argv[0])                          # プログラム名を表示する

if len(argv) == 1:                      # 取得した引数が1個(プログラム名のみ)のとき
    print('Hello, World!')              # 文字列 Hello, World! を出力する

else:                                   # そうでないとき(引数がある時)
    for name in argv[1:]:               # 1番目以降の引数を変数nameへ代入
        print('Hello,', name + '!')     # 変数nameの内容を、文字列Helloに続いて表示
