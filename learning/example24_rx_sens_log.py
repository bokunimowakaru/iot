#!/usr/bin/env python3
# coding: utf-8
# Example 24 各種IoTセンサ用・測定結果表示プログラム【保存機能つき】

sensors = [\
    'temp0','hall0','adcnv','btn_s','pir_s','illum',\
    'temp.','humid','press','envir','accem','rd_sw',\
    'press','e_co2'\
]                                                       # 対応センサリスト

import socket
import datetime

def check_dev_name(s):                                  # デバイス名を取得
    if s.isprintable() and len(s) == 7 and s[5] == '_': # 形式が一致する時
        for dev in sensors:                             # センサリストの照合
            if s[0:5] == dev:                           # デバイス名が一致
                return s                                # デバイス名を応答
    return None                                         # Noneを応答

def get_val(s):                                         # データを数値に変換
    s = s.replace(' ','')                               # 空白文字を削除
    if s.replace('.','').replace('-','').isnumeric():   # 文字列が数値を示す
        return float(s)                                 # 小数値を応答
    return None                                         # Noneを応答

def save(filename, data):
    try:
        fp = open(filename, mode='a')                   # 書込用ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
    fp.write(data + '\n')                               # dataをファイルへ
    fp.close()                                          # ファイルを閉じる

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

try:
    while sock:                                         # 永遠に繰り返す
        udp = sock.recv(64).decode().strip()            # UDPパケットを取得
        vals = udp.split(',')                           # 「,」で分割
        num = len(vals)                                 # データ数の取得
        dev = check_dev_name(vals[0])                   # デバイス名を取得
        if not dev or num < 2:                          # 不適合orデータなし
            continue                                    # whileに戻る
        date=datetime.datetime.today()                  # 日付を取得
        s = date.strftime('%Y/%m/%d %H:%M')+', '+dev    # 日付を変数sへ代入
        for i in range(1,num):                          # データ回数の繰り返し
            val = get_val(vals[i])                      # データを取得
            s += ', '                                   # 「,」を追加
            if val is not None:                         # データがある時
                s += str(val)                           # データを変数sに追加
        filename = dev + '.csv'                         # ファイル名を作成
        print(s, '-> ' + filename, flush=True)          # 受信データを表示
        save(filename, s)                               # ファイルへ保存

except KeyboardInterrupt:                               # キー割り込み発生時
    print('\nKeyboardInterrupt')                        # キーボード割り込み表示
    sock.close()                                        # ソケットの終了
    exit()                                              # プログラムの終了

'''
pi@raspberrypi:~/iot/learning $ ./example24_rx_sens_log.py
Listening UDP port 1024 ...
2019/06/16 15:22, temp0_2, 16.0 -> temp0_2.csv
2019/06/16 15:22, pir_s_2, 1.0 -> pir_s_2.csv
2019/06/16 15:22, humid_2, 30.0, 52.0 -> humid_2.csv
'''
