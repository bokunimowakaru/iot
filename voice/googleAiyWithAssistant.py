#!/usr/bin/env python3

# coding: utf-8

# Google AIY Voice Kit V1 用 Google Home のような Assistant Library Demo
#
# ※ 本プログラムを動作させるには、Google Assistantの設定が必要です
# 
# Copyright (c) 2019 Wataru KUNINO

##############################################################################################
# 以下のライセンスのソースコードを改変して製作しました。

##############################################################################################
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Activates the Google Assistant with hotword detection, using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio.

.. note:

    This example depends on hotword detection (such as "Okay Google") to activate the Google
    Assistant, which is supported only with Raspberry Pi 2/3. If you're using a Pi Zero, this
    code won't work. Instead, you must use the button or another type of trigger, as shown
    in assistant_library_with_button_demo.py.
"""
##############################################################################################

import logging
import platform
import sys
import subprocess   # for power off and reboot raspberry pi

from google.assistant.library.event import EventType

from aiy.assistant import auth_helpers
from aiy.assistant.library import Assistant
from aiy.board import Board, Led
from aiy.voice import tts

def say(message):
    try:                                                    # 例外処理の監視を開始
        tts.say(message,lang='en-US')
        # tts.say(message,lang='ja-JP')  # ja-JPには対応していない(lib 1.0.0)
    except Exception as e:
        print(e)                                            # エラー内容を表示

def process_event(assistant, led, event):
    logging.info(event)

    if event.type == EventType.ON_START_FINISHED:
        led.state = Led.BEACON_DARK  # Ready.
        logging.info('Say "OK, Google" then speak, or press Ctrl+C to quit...')
        say('Say OK Google, then speak, or say OK Google Shoe Ryou to quit')
        say('Kontiwa. key doll, she ma she tar.')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        led.state = Led.ON  # Listening.

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        led.state = Led.PULSE_QUICK  # Thinking.

    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        led.state = Led.BEACON_DARK

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if (text == 'power off' or text == 'パワーオフ'):
            assistant.stop_conversation()
            say('Good bye!')
            subprocess.call('sudo shutdown now', shell=True)
            return 1
        elif (text == 'reboot' or text == '再起動'):
            assistant.stop_conversation()
            say('See you in a bit!')
            subprocess.call('sudo reboot', shell=True)
            return 1
        elif (text.find('ip address') >= 0 or text.find('ip アドレス') >= 0):
            assistant.stop_conversation()
            ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
            say('My IP address is %s' % ip_address.decode('utf-8'))
        elif (text =='testing' or text == 'テスト'):
            assistant.stop_conversation()
            say('This is test')
        elif (text =='good bye' or text == '終了'):
            assistant.stop_conversation()
            say('I will come back to life, when you will restart this example script. See you.')
            return 1
    return 0

def main():
    logging.basicConfig(level=logging.INFO)

    credentials = auth_helpers.get_assistant_credentials()
    with Board() as board, Assistant(credentials) as assistant:
        for event in assistant.start():
            if process_event(assistant, board.led, event) > 0:
                break
    say('D war, sir yoo nara') 

if __name__ == '__main__':
    main()
