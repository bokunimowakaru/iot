#!/usr/bin/env python3
# coding: utf-8
# Example 04 コンピュータは計算機。四則演算を行ってみよう

from sys import argv                    # 本プログラムの引数argvを取得する

A = 1                                   # 変数Aへ1を代入
B = 2                                   # 変数Bへ2を代入
print(argv[0])                          # プログラム名を表示する

if len(argv) > 1:                       # プログラム名以外の引数が1個以上の時
    A = int(argv[1])                    # 変数Aに第1引数を代入

if len(argv) > 2:                       # プログラム名以外の引数が2個以上の時
    B = int(argv[2])                    # 変数Bに第2引数を代入

print(A, '＋', B, '＝', A + B)          # A ＋ B を計算して表示する
print(A, '－', B, '＝', A - B)          # A － B を計算して表示する
print(A, '×', B, '＝', A * B)          # A × B を計算して表示する
print(A, '÷', B, '＝', A / B)          # A ÷ B を計算して表示する
