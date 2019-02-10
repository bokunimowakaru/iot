#!/usr/bin/env python3
# coding: utf-8

# Google AIY Voice Kit用 【ちょっとだけ会話版】
# 音声「LED ON」や「LED OFF」でUDPを送信する
# aiy.voiceが日本語の音声出力に対応していなかったので、英語による暫定版
# Copyright (c) 2019 Wataru KUNINO

from aiy.cloudspeech import CloudSpeechClient               # AIY音声認識用ライブラリ
from aiy.board import Board,Led                             # AIYキット用ライブラリ
from aiy.voice import tts
import socket                                               # UDP送信用ライブラリ
import subprocess

device = 'voice_1'                                          # UDP送信用のデバイス名
port = 1024                                                 # UDPポート番号

vclient = CloudSpeechClient()                               # 音声認識用 vclient の生成
board = Board()                                             # AIYキット用 board の生成
board.led.state = Led.BLINK                                 # LEDを点滅させる
talk = [
    'Hello',
    'I\'m waiting for your voice commands.',
    'Please say LED on, or off, to send udp message.',
    'Tell me stop, if you have done testing VR.',
    '']
tts.say(talk[0],lang='en-US')
talk_n=1

while True:
    udp = None                                              # 送信データ用変数udpを定義
    voice = vclient.recognize(language_code='en-US')        # 日本語による音声認識
    if voice == None:                                       # 音声データが無かったとき
        if talk[talk_n] != '':
            tts.say(talk[talk_n],lang='en-US')
            talk_n += 1
        continue                                            # whileループの先頭に戻る
    print('recognized =',voice)                             # 認識結果を表示する
    if 'STOP' in voice.upper():                             # 音声「STOP」を認識したとき
        tts.say('stopped VR, good bye',lang='en-US')
        break                                               # whileループを抜ける
    if 'LED' in voice.upper():                              # 音声「LED」を認識したとき
        board.led.state = Led.BLINK                         # LEDを点滅させる
        if 'OFF' in voice.upper():                          # かつ「OFF」を認識したとき
            board.led.state = Led.OFF                       # LEDをOFFする
            tts.say('turned off the LED',lang='en-US')
            udp = device + ', 0'                            # 変数udpへ送信データを代入
        if 'ON' in voice.upper():                           # 音声「ON」時
            board.led.state = Led.ON                        # LEDをONする
            tts.say('turned on the LED',lang='en-US')
            udp = device + ', 1'                            # 変数udpへ送信データを代入
    if 'HELLO' in voice.upper() or 'HEY' in voice.upper():  # 音声「HELLO」を認識したとき
        tts.say(talk[0],lang='en-US')
        talk_n=1
    if 'shut down' in voice
        tts.say('shuting down your raspberry pi, see you again.',lang='en-US')
        subprocess.call('sudo shutdown now', shell=True)
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
exit
