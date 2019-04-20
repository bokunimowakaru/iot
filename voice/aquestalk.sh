#!/bin/bash
# coding: utf-8

# AquesTalk 起動用スクリプト
# Copyright (c) 2019 Wataru KUNINO

if [ ! -e "./aquestalkpi/AquesTalkPi" ]; then
    echo "AquesTalkをインストールしてください。"
    exit
fi

if [ $# -ge 2 ]; then
    if [ "${1}" == "-f" ]; then
        echo "TALK:" ${2}
        aquestalkpi/AquesTalkPi -f ${2} |aplay
    fi
elif [ $# -eq 1 ]; then
    echo "TALK:" ${1}
    aquestalkpi/AquesTalkPi "${1}" |aplay
fi
echo "Done" ${0}
exit
