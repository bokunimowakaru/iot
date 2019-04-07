#!/usr/bin/env python3
# coding: utf-8
# Example 05 コンピュータの体温を測って表示してみよう

filename = '/sys/class/thermal/thermal_zone0/temp' # 温度ファイル

fp = open(filename)                 # 温度ファイルを開く
temp = float(fp.read()) / 1000      # ファイルを読み込み1000で除算する
fp.close()                          # ファイルを閉じる
print('Temperature =',temp)         # 温度を表示する
