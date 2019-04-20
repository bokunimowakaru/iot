#!/bin/bash
# coding: utf-8

# Julius用
# 音声「LEDの電源をON」や「LEDの電源をOFF」でUDPを送信する
# 「アプリを終了して」と話した後に、一声かけると終了する
# Copyright (c) 2019 Wataru KUNINO

./juliusBase.sh | ./juliusSpeechToUdp.py SUBPROCESS
echo "Done" ${0}
exit
