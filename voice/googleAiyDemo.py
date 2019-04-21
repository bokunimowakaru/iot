#!/usr/bin/env python3
# coding: utf-8

# Google AIY Voice Kit会話デモ
# 音声「こんにちは」で「はい、こんにちは」を、
# 音声「お元気ですか？」で「はい、元気です」を、
# 音声「あなたの名前は？」で「私の名前はJuriusです」を、
# 「アプリを終了して」で「さようなら」の会話が出来ます。
# Copyright (c) 2019 Wataru KUNINO

from aiy.cloudspeech import CloudSpeechClient               # AIY音声認識用ライブラリ
from aiy.board import Board,Led                             # AIYキット用ライブラリ
import aiy.voice.tts

vclient = CloudSpeechClient()                               # 音声認識用 vclient の生成
board = Board()                                             # AIYキット用 board の生成
print('準備完了')                                           # 準備完了と表示する
aiy.voice.tts.say('key doll, she ma she tar',lang='en-US')  # ja-JPには対応していない

while True:
    board.led.state = Led.BLINK                             # LEDを点滅させる
    voice = vclient.recognize(language_code='ja_JP')        # 日本語による音声認識
    board.led.state = Led.ON                                # LEDをONする
    if voice == None:                                       # 音声データが無かったとき
        continue                                            # whileループの先頭に戻る
    print('認識結果 =',voice)                               # 認識結果を表示する
    if '終了' in voice:                                     # 音声「終了」を認識したとき
        break                                               # whileループを抜ける
    if 'こんにちは' in voice:                               # 音声「こんにちは」認識時
        aiy.voice.tts.say('hi, kontiwa',lang='en-US')       # 「はい、こんにちは」を回答
    if '元気' in voice:                                     # 音声「元気」を認識したとき
        aiy.voice.tts.say('hi, genki death',lang='en-US')   # 「はい、元気です」を回答
    if '名前' in voice:                                     # 音声「元気」を認識したとき
        aiy.voice.tts.say('wata she war, google cloud speech death',lang='en-US') 
    if 'さようなら' in voice or 'さよなら' in voice :
        aiy.voice.tts.say('shoeryo through tolkey war, shoeryo tou her nacy techda psy')

aiy.voice.tts.say('D war, sir yoo nara',lang='en-US')       # 「では、さようなら」を回答
board.close()                                               # Google AIYキットのGPIO開放
exit
