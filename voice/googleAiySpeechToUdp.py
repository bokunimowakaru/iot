#!/usr/bin/env python3
# coding: utf-8

# Google AIY Voice Kit用
# 音声「LEDをON」や「LEDをOFF」でUDPを送信する
# Copyright (c) 2019 Wataru KUNINO

from aiy.cloudspeech import CloudSpeechClient               # AIY音声認識用ライブラリ
from aiy.board import Board,Led                             # AIYキット用ライブラリ
import socket                                               # UDP送信用ライブラリ

device = 'voice_1'                                          # UDP送信用のデバイス名
port = 1024                                                 # UDPポート番号

vclient = CloudSpeechClient()                               # 音声認識用 vclient の生成
board = Board()                                             # AIYキット用 board の生成
board.led.state = Led.BLINK                                 # LEDを点滅させる
print('準備完了')                                           # 準備完了と表示する

while True:
    udp = None                                              # 送信データ用変数udpを定義
    voice = vclient.recognize(language_code='ja_JP')        # 日本語による音声認識
    if voice == None:                                       # 音声データが無かったとき
        continue                                            # whileループの先頭に戻る
    print('認識結果 =',voice)                               # 認識結果を表示する
    if '終了' in voice:                                     # 音声「終了」を認識したとき
        break                                               # whileループを抜ける
    if 'LED' in voice.upper():                              # 音声「LED」を認識したとき
        board.led.state = Led.BLINK                         # LEDを点滅させる
        if 'オフ' in voice or '4' in voice:                 # 「OFF」を認識したとき
            board.led.state = Led.OFF                       # LEDをOFFする
            udp = device + ', 0'                            # 変数udpへ送信データを代入
        if 'オン' in voice or '音' in voice or 'ON' in voice.upper():   # 音声「ON」時
            board.led.state = Led.ON                        # LEDをONする
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
board.close()                                               # Google AIYキットのGPIO開放
exit()
