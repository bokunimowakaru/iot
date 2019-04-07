#!/usr/bin/env python3
# coding: utf-8
# Example 06 コンピュータの体温を測って表示してみよう 【例外処理対応版】

filename = '/sys/class/thermal/thermal_zone0/temp'      # 温度ファイル

try:                                                    # 例外処理の監視を開始
    fp = open(filename)                                 # 温度ファイルを開く

except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

temp = float(fp.read()) / 1000      # ファイルを読み込み1000で除算する
fp.close()                          # ファイルを閉じる
print('Temperature =',temp)         # 温度を表示する
