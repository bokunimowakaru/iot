#!/usr/bin/env python3
# coding: utf-8

import sys
import subprocess

ir_in_port  = 4                                 # GPIO ポート番号
ir_type     = 'AEHA'                            # 赤外線方式 AEHA/NEC/SIRC/AUTO
ir_wait_sec = -1                                # 最大待ち受け時間(-1で∞)

path = './raspi_ir_in'                          # IR 受信ソフトモジュールのパス
ir_types = ['AEHA','NEC','SIRC','AUTO']         # 赤外線リモコン方式名の一覧表
try:
    type_i = ir_types.index(ir_type)            # タイプ名の参照番号
except ValueError as e:                         # 例外処理発生時(アクセス拒否)
    print('ERROR:ir_types,',e)                  # エラー内容表示
    type_i = 255                                # 赤外線リモコン方式を自動に設定
if type_i ==3:                                  # AUTOのとき
    type_i = 255                                # 赤外線リモコン方式を自動に設定
app = [path, str(ir_in_port), str(type_i), str(ir_wait_sec)]    # 起動設定を集約

print('raspi_ir_in, app =', app)                # サブ起動する設定内容を表示

while True:                                             # 以下を繰り返し実行
    res = subprocess.run(app, stdout=subprocess.PIPE)   # サブプロセスとして起動
    data = res.stdout.decode().strip()                  # 結果をdataへ代入
    code = res.returncode                               # 終了コードをcodeへ代入
    leng = round((len(data)+1)/3)                       # 受信コード長をlengへ
    if code != 0 or leng < 3:                           # 受信長3未満やエラー時
        print('ret =', code, 'len =', leng)             # 結果を表示
        continue                                        # whileに戻る
    print('ret=', code, ', len=', leng, ', ', data)     # 結果データを表示

'''
実行結果例
pi@raspberrypi:~/iot/ir-remote $ ./raspi_ir_in.py
raspi_ir_in, app = ['./raspi_ir_in', '4', '0', '-1']
ret= 0 , len= 6 ,  AA 5A 8F 12 15 E1
ret= 0 , len= 6 ,  AA 5A 8F 12 14 F1

'''
