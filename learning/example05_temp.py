#!/usr/bin/env python3
# coding: utf-8
# Example 05 コンピュータの体温を測って表示してみよう

fp = open('/sys/class/thermal/thermal_zone0/temp') # 温度ファイルを開く
if fp:                                  # ファイルを開くことに成功したとき
    temp = float(fp.read()) / 1000      # ファイルを読み込み1000で除算する
    fp.close                            # ファイルを閉じる
    print('Temperature =',temp)         # 温度を表示する
