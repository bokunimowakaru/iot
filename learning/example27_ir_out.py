#!/usr/bin/env python3
# coding: utf-8

# Example 27 赤外線リモコン送信機

import sys
sys.path.append('../libs/ir_remote')
import raspi_ir

ir_code     = ['aa','5a','8f','12','16','d1']   # リモコンコード

raspiIr = raspi_ir.RaspiIr('AEHA',out_port=4)   # 家製協方式で GPIO 4 を使用
                                                # 第1引数='AEHA','NEC','SIRC'
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
