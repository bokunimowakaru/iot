#!/bin/bash
# coding: utf-8

# Julius 会話デモ
# 音声「こんにちは」で「はい、こんにちは」を、
# 音声「お元気ですか？」で「はい、元気です」を、
# 音声「あなたの名前は？」で「私の名前はJuriusです」を、
# 「アプリを終了して」で「さようなら」の会話が出来ます。
# Copyright (c) 2019 Wataru KUNINO

./juliusBase.sh | ./juliusDemo.py SUBPROCESS
echo "Done" ${0}
exit
