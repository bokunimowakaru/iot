#!/usr/bin/env python3
# coding: utf-8

# Google AIY Voice Kit用 LED制御
# 音声「LED ON」や「LED OFF」でLEDを制御する
# Copyright (c) 2019 Wataru KUNINO

from aiy.cloudspeech import CloudSpeechClient               # AIY音声認識用ライブラリ
from aiy.board import Board,Led                             # AIYキット用ライブラリ

vclient = CloudSpeechClient()                               # 音声認識用 vclient の生成
board = Board()                                             # AIYキット用 board の生成
board.led.state = Led.BLINK                                 # LEDを点滅させる
print('準備完了')                                           # 準備完了と表示する

while True:
    voice = vclient.recognize(language_code='ja_JP')        # 日本語による音声認識
    if voice == None:                                       # 音声データが無かったとき
        continue                                            # whileループの先頭に戻る
    print('認識結果 =',voice)                               # 認識結果を表示する
    if '終了' in voice:                                     # 音声「終了」を認識したとき
        break                                               # whileループを抜ける
    if 'LED' in voice.upper():                              # 音声「LED」を認識したとき
        if 'オフ' in voice or '4' in voice:                 # 「OFF」を認識したとき
            board.led.state = Led.OFF                       # LEDをOFFする
        if 'オン' in voice or '音' in voice or 'ON' in voice.upper():   # 音声「ON」時
            board.led.state = Led.ON                        # LEDをONする
board.close()                                               # Google AIYキットのGPIO開放
