# coding: utf-8
# UDPを受信する for MicroPython
# Copyright (c) 2018-2019 Wataru KUNINO

# Error ENOMEM や EADDRINUSE が出た場合はハードウェアリセットを実行してください
#   machine.reset()

port = 1024
buf_n= 128                                              # 受信バッファ容量(バイト)

import network
import socket

pyb.LED(1).on()
eth = network.Ethernet()
try:
    eth.active(True)
    eth.ifconfig('dhcp')
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('',port))                                # ソケットに接続
    print('Listening UDP port', port, '...')            # ポート番号表示
except Exception as e:                                  # 例外処理発生時
    pyb.LED(3).on()
    while True:
        print(e)                                        # エラー内容を表示
        pyb.delay(3000)

while sock:                                             # 永遠に繰り返す
    udp, udp_from = sock.recvfrom(buf_n)                # UDPパケットを取得
    udp = udp.decode()                                  # UDPデータを文字列に変換
    pyb.LED(2).on()
    s=''                                                # 表示用の文字列変数s
    for c in udp:                                       # UDPパケット内
        if ord(c) >= ord(' ') and ord(c) <= ord('~'):   # 表示可能文字
            s += c                                      # 文字列sへ追加
    print(udp_from[0] + ', ' + s)                       # 受信データを出力
    pyb.LED(2).off()
sock.close()                                            # ソケットの切断
pyb.LED(1).off()
