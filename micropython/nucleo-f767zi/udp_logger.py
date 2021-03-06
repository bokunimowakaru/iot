# coding: utf-8
# UDPを受信する for MicroPython
# Copyright (c) 2018-2019 Wataru KUNINO

# Error ENOMEM や EADDRINUSE が出た場合はハードウェアリセットを実行してください
#   machine.reset()

port = 1024                                             # UDPポート番号
buf_n= 128                                              # 受信バッファ容量(バイト)

import network                                          # ネットワーク通信
import socket                                           # ソケット通信

pyb.LED(1).on()                                         # LED(緑色)を点灯
eth = network.Ethernet()                                # Ethernet用のethを生成
try:
    eth.active(True)                                    # Ethernetを起動
    eth.ifconfig('dhcp')                                # DHCPクライアントを設定
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('',port))                                # ソケットに接続
    print('Listening UDP port', port, '...')            # ポート番号表示
except Exception as e:                                  # 例外処理発生時
    pyb.LED(3).on()                                     # LED(赤色)を点灯
    while True:
        print(e)                                        # エラー内容を表示
        pyb.delay(3000)                                 # 3秒の待ち時間処理

while sock:                                             # 永遠に繰り返す
    udp, udp_from = sock.recvfrom(buf_n)                # UDPパケットを取得
    udp = udp.decode()                                  # UDPデータを文字列に変換
    pyb.LED(2).on()                                     # LED(青色)を点灯
    s=''                                                # 表示用の文字列変数s
    for c in udp:                                       # UDPパケット内
        if ord(c) >= ord(' ') and ord(c) <= ord('~'):   # 表示可能文字
            s += c                                      # 文字列sへ追加
    if s == 'Ping':                                     # 受信データがPingの時
        pyb.LED(1).off()                                # LED(緑色)を消灯
        pyb.LED(3).on()                                 # LED(赤色)を点灯
    if s == 'Pong':                                     # 受信データがPongの時
        pyb.LED(1).on()                                 # LED(緑色)を点灯
        pyb.LED(3).off()                                # LED(赤色)を消灯
    print(udp_from[0] + ', ' + s)                       # 受信データを出力
    pyb.LED(2).off()
sock.close()                                            # ソケットの切断
pyb.LED(1).off()
