#!/usr/bin/env python3
# coding: utf-8

# Example 27 赤外線リモコン送信機

from sys import argv                            # 引数argvを取得する
import sys
sys.path.append('../libs/ir_remote')
import raspi_ir

ir_type     = 'AEHA'                            # 'AEHA','NEC','SIRC'
ir_code     = ['aa','5a','8f','12','16','d1']   # リモコンコード

print('Usage:', argv[0], 'type [data]')         # プログラム名と使い方
if len(argv) >= 2:                              # 第1引数が存在
    ir_type = argv[1]                           # 第1引数を変数ir_typeへ
if len(argv) >= 3:                              # 第2引数が存在
    ir_code = argv[2:]                          # 引数を変数ir_codeへ

raspiIr = raspi_ir.RaspiIr(ir_type,out_port=4)  # GPIO 4 を使用
try:
    ret = raspiIr.output(ir_code)               # リモコンコードを送信
except ValueError as e:                         # 例外処理発生時(アクセス拒否)
    print('ERROR:raspiIr,',e)                   # エラー内容表示
print(raspiIr.code)                             # 送信済の内容を表示

'''
実行結果例
pi@raspberrypi:~/iot/learning $ ./example27_ir_out.py
['aa', '5a', '8f', '12', '16', 'd1']
'''
