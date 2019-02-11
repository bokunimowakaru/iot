#!/usr/bin/env python3
# coding: utf-8

# Julius用
# 音声「LEDの電源をON」や「LEDの電源をOFF」でUDPを送信する
# 「アプリを終了する」で終了する
# Copyright (c) 2019 Wataru KUNINO

import sys
import socket                                               # UDP送信用ライブラリ
import subprocess
from time import sleep

julius_path_main_conf  = "/home/pi/julius/dictation-kit-v4.4/main.jconf"
julius_path_amgmm_conf = "/home/pi/julius/dictation-kit-v4.4/am-gmm.jconf"
julius_com = ['./juliusSpeechToUdp.sh']
julius_com.append(julius_path_main_conf)
julius_com.append(julius_path_amgmm_conf)
# print('julius_com = ',julius_com)

device = 'voice_1'                                          # UDP送信用のデバイス名
port = 1024                                                 # UDPポート番号
mode = 0

argc = len(sys.argv)                                    # 引数の数をargcへ代入
print('Usage: '+sys.argv[0]+' main amgmm subpro)')      # タイトル表示
if argc == 3:                                           # 入力パラメータ数の確認
    julius_path_main_conf = sys.argv[1]
    julius_path_amgmm_conf = sys.argv[2]
if argc > 1:
    if 'SUBPRO' in sys.argv[argc - 1].upper():
        mode = 1
if mode == 0:
    julius = subprocess.run(julius_com, shell=True)
    exit

while mode == 1:
    for line in sys.stdin:                              # 標準入力から変数lineへ
        udp = None                                              # 送信データ用変数udpを定義
        sp = line.find(':')
        if sp < 4 or len(line) < sp + 2:
            continue                                            # forループの先頭に戻る
        com = line[0:sp]
        if 'STAT' in com.upper() or 'PASS' in com.upper():
            print(line.strip())
            continue                                            # forループの先頭に戻る
        if 'SENTENCE' in com.upper():
            voice = line[sp+1:].strip()
            print('SENTENCE=',voice)
            if '終了' in voice:                                     # 音声「終了」を認識したとき
                mode = 0
                break                                               # whileループを抜ける
            if 'ＬＥＤ' in voice:                              # 音声「LED」を認識したとき
                if 'オフ' in voice:                 # 「OFF」を認識したとき
                    udp = device + ', 0'                            # 変数udpへ送信データを代入
                if 'オン' in voice:   # 音声「ON」時
                    udp = device + ', 1'                            # 変数udpへ送信データを代入
            if udp == None:                                         # 変数udpがNodeのとき
                continue                                            # whileループの先頭に戻る
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)   # ソケット接続を行う
            if sock:                                                # ソケット接続に成功したとき
                print('send : ' + udp)                              # 受信データを出力
                udp=(udp + '\n').encode()                           # バイト列に変換
                sock.sendto(udp,('255.255.255.255',port))           # UDPブロードキャスト送信
                sock.close()                                        # ソケットの切断
print('終了')
exit
