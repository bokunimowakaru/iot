#!/usr/bin/env python3
# coding: utf-8

# Example 26 IoT赤外線リモコン信号を受信する

import socket                                           # IP通信用モジュール

def check_dev_name(s):                                  # デバイス名を取得
    if s.isprintable() and len(s) == 7 \
        and s[0:6] == 'ir_in_':                         # IoT赤外線リモコン
        return s                                        # デバイス名を応答
    return None                                         # Noneを応答

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print('ERROR, Sock:',e)                             # エラー内容を表示
    exit()                                              # プログラムの終了

while sock:                                             # 永遠に繰り返す
    udp, udp_from = sock.recvfrom(64)                   # UDPパケットを取得
    vals = udp.decode().strip().split(',')              # 「,」で分割
    dev = check_dev_name(vals[0])                       # デバイス名を取得
    if dev and len(vals) >= 2:                          # 取得成功かつ項目2以上
        print(vals[0],udp_from[0],',',vals[1:])         # リモコンコードを出力

'''
実行例
--------------------------------------------------------------------------------
pi@raspberrypi:~/iot/learning $ ./example26_rx_ir_in.py
Listening UDP port 1024 ...
ir_in_2 192.168.0.170 , ['48', 'a5', '50', '88', '13', '17', 'de']
ir_in_2 192.168.0.170 , ['48', 'a5', '50', '88', '13', '16', 'e0']
ir_in_2 192.168.0.170 , ['48', 'a5', '50', '88', '13', '15', 'f1']

--------------------------------------------------------------------------------
'''
