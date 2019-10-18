#!/usr/bin/env python3
# coding: utf-8

import sys
import subprocess

ir_in_port  = 4                                 # GPIO ポート番号
ir_type     = 'AEHA'                            # 赤外線方式 AEHA/NEC/SIRC
ir_code     = ['aa','5a','8f','12','16','d1']   # リモコンコード(スペース区切り)

path = './raspi_ir_out'                         # IR 送信ソフトモジュールのパス
ir_types = ['AEHA','NEC','SIRC']                # 赤外線リモコン方式名の一覧表
try:
    type_i = ir_types.index(ir_type)            # タイプ名の参照番号
except ValueError as e:                         # 例外処理発生時(アクセス拒否)
    print('ERROR:ir_types,',e)                  # エラー内容表示
    exit()
app = [path, str(ir_in_port), str(type_i)]      # 起動設定を集約
for code in ir_code:
    app.append(code)
print('raspi_ir_in, app =', app)                # サブ起動する設定内容を表示

res = subprocess.run(app,stdout=subprocess.PIPE)# サブプロセスとして起動
data = res.stdout.decode().strip()              # 結果をdataへ代入
code = res.returncode                           # 終了コードをcodeへ代入
print('ret=', code, ', ', data)                 # 結果データを表示

'''
実行結果例
pi@raspberrypi4:~/iot/learning $ ./example27_ir_out.py
raspi_ir_in, app = ['../tools/ir-remote/raspi_ir_out','4','0','aa','5a','8f','12','16','d1']
ret= 0 ,  Pin = 7, Port(BCM) = 4 Port(wPi) = 7
mode = 0
data[6] = AA 5A 8F 12 16 D1

'''
