#!/usr/bin/env python3
# coding: utf-8
# Example 21 IoT温度計から温度値を受信し、【保存】する

filename = 'temp.csv'                                   # 温度ファイル

import socket
import datetime

def check_dev_name(s):                                  # デバイス名を取得
    if s.isprintable() and len(s) == 7 \
        and s[0:4] == 'temp' and s[5] == '_':           # IoT温度計に一致する時
        return s                                        # デバイス名を応答
    return None                                         # Noneを応答

def get_val(s):                                         # データを数値に変換
    s = s.replace(' ','')                               # 空白文字を削除
    if s.replace('.','').replace('-','').isnumeric():   # 文字列が数値を示す
        return float(s)                                 # 小数値を応答
    return None                                         # Noneを応答

try:
    fp = open(filename, mode='a')                       # 書込用ファイルを開く
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

try:
    while sock:                                         # 永遠に繰り返す
        udp = sock.recv(64).decode().strip()            # UDPパケットを取得
        vals = udp.split(',')                           # 「,」で分割
        dev = check_dev_name(vals[0])                   # デバイス名を取得
        if dev and len(vals) >= 2:                      # 取得成功かつ項目2以上
            val = get_val(vals[1])                      # データ1番目を取得
            date=datetime.datetime.today()              # 日付を取得
            s = date.strftime('%Y/%m/%d %H:%M') + ', '  # 日付を変数sへ代入
            s += udp                                    # 受信データを追加
            fp.write(s + '\n')                          # 受信結果をファイルへ
            print(s, '-> ' + filename, end='')          # 受信データを表示
            print(', temperature =',val, flush=True)    # 取得値valを表示

except KeyboardInterrupt:                               # キー割り込み発生時
    print('\nKeyboardInterrupt')                        # キーボード割り込み表示
    sock.close()                                        # ソケットの終了
    fp.close()                                          # ファイルを閉じる
    exit()                                              # プログラムの終了
