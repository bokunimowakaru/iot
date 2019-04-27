#!/bin/bash
# coding: utf-8

# Julius 音声時計
# 音声「今何時？」でインターネットから時刻を取得して、回答します。

./juliusBase.sh | ./juliusClock.py SUBPROCESS
echo "Done" ${0}
exit
