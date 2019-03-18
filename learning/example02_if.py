#!/usr/bin/env python3
# coding: utf-8
# Example 02 もしもif ～ さもなければelse ～

from sys import argv                    # 本プログラムの引数argvを取得する

print(argv[0])                          # プログラム名を表示する

if len(argv) == 1:                      # 取得した引数が1個(プログラム名のみ)のとき
    print('Hello, World!')              # 文字列 Hello, World! を出力する

else:                                   # そうでないとき(引数がある時)
    print('Hello,', argv[1] + '!')      # 1番目の引数を、文字列Helloに続いて表示する
