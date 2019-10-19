#!/usr/bin/env python3
# coding: utf-8

# Example 27 IoT赤外線リモコン送信機

import sys
sys.path.append('../libs/ir_remote')
import raspi_ir

ir_code     = ['aa','5a','8f','12','16','d1']   # リモコンコード

raspiIr = raspi_ir.RaspiIr('AEHA',out_port=18)  # 家製協方式で GPIO 18 を使用
try:
    ret = raspiIr.output(ir_code)               # リモコンコードを送信
except ValueError as e:                         # 例外処理発生時(アクセス拒否)
    print('ERROR:raspiIr,',e)                   # エラー内容表示
print('ret =', ret)                             # 送信したリモコン信号を表示

'''
実行結果例
pi@raspberrypi4:~/iot/learning $ ./example27_ir_out.py
raspi_ir_in, app = ['../tools/ir-remote/raspi_ir_out','4','0','aa','5a','8f','12','16','d1']
ret= 0 ,  Pin = 7, Port(BCM) = 4 Port(wPi) = 7
mode = 0
data[6] = AA 5A 8F 12 16 D1
code = ['aa', '5a', '8f', '12', '16', 'd1']
'''
