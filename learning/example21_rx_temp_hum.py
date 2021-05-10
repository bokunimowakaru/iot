#!/usr/bin/env python3
# coding: utf-8
# Example 21 IoT温度計から温度値を受信し、表示する 【湿度の取得に対応】

sensors = ['temp.','temp0','humid','press','envir'] # 対応センサのデバイス名

import socket

def check_dev_name(s):                                  # デバイス名を取得
    if not s.isprintable():                             # 表示可能な文字列で無い
        return None                                     # Noneを応答
    if len(s) != 7 or s[5] != '_':                      # フォーマットが不一致
        return None                                     # Noneを応答
    for sensor in sensors:                              # デバイスリスト内
        if s[0:5] == sensor:                            # センサ名が一致したとき
            return s                                    # デバイス名を応答
    return None                                         # Noneを応答

def get_val(s):                                         # データを数値に変換
    s = s.replace(' ','')                               # 空白文字を削除
    try:                                                # 小数変換の例外監視
        return float(s)                                 # 小数に変換して応答
    except ValueError:                                  # 小数変換失敗時
        return None                                     # Noneを応答

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
        print('device =',vals[0],udp_from[0],', temperature =',val,end='')
        if len(vals) >= 3:                              # 項目3以上
           val = get_val(vals[2])                       # データ2番目を取得
           if dev == 'press':                           # IoT気圧計の時
               print(', pressure =', val ,end='')       # 気圧を表示
           else:                                        # IoT温湿度計・環境の時
               print(', humidity =', val ,end='')       # 湿度を表示
        if len(vals) >= 4:                              # 項目4以上
           val = get_val(vals[3])                       # データ3番目を取得
           print(', pressure =', val ,end='')           # 気圧を表示
        print()                                         # 改行を表示

'''
pi@raspberrypi:~/iot/learning $ ./example21_rx_temp.py
Listening UDP port 1024 ...
device = temp0_2 192.168.0.8 , temperature = 16.0
device = temp0_2 192.168.0.8 , temperature = 16.0
device = temp0_2 192.168.0.8 , temperature = 16.0
'''
