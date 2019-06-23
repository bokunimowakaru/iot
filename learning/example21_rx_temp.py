#!/usr/bin/env python3
# coding: utf-8
# Example 21 IoT温度計から温度値を受信し、表示する

import socket

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

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while sock:                                             # 永遠に繰り返す
    udp, udp_from = sock.recvfrom(64)                   # UDPパケットを取得
    vals = udp.decode().strip().split(',')              # 「,」で分割
    dev = check_dev_name(vals[0])                       # デバイス名を取得
    if dev and len(vals) >= 2:                          # 取得成功かつ項目2以上
        val = get_val(vals[1])                          # データ1番目を取得
        print('device =',vals[0],udp_from[0],', temperature =',val) # 表示

'''
pi@raspberrypi:~/iot/learning $ ./example21_rx_temp.py
Listening UDP port 1024 ...
device = temp0_2 192.168.0.8 , temperature = 16.0
device = temp0_2 192.168.0.8 , temperature = 16.0
device = temp0_2 192.168.0.8 , temperature = 16.0
'''
