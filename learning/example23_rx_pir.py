#!/usr/bin/env python3
# coding: utf-8
# Example 23 IoT人感センサを受信する

import socket

def check_dev_name(s):                                  # デバイス名を取得
    if s.isprintable() and len(s) == 7 \
        and s[0:5] == 'pir_s' and s[5] == '_':          # IoT人感センサに一致
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
    udp = sock.recv(64).decode().strip()                # UDPパケットを取得
    vals = udp.split(',')                               # 「,」で分割
    dev = check_dev_name(vals[0])                       # デバイス名を取得
    if dev and len(vals) >= 2:                          # 取得成功かつ項目2以上
        val = get_val(vals[1])                          # データ1番目を取得
        if val:                                         # val=1のとき
            print('device =',vals[0],', pir =',val)     # 取得値を表示

'''
pi@raspberrypi:~/iot/learning $ ./example23_rx_pir.py
Listening UDP port 1024 ...
device = pir_s_2 , pir = 1.0
device = pir_s_2 , pir = 1.0
device = pir_s_2 , pir = 1.0
'''
