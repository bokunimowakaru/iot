#!/bin/bash
# coding: utf-8

julius_path_main_conf="/home/pi/julius/dictation-kit-v4.4/main.jconf"
julius_path_amgmm_conf="/home/pi/julius/dictation-kit-v4.4/am-gmm.jconf"
julius_com="/usr/local/bin/julius"

card=`arecord -l|grep "USB Audio"|tail -1|cut -d" " -f2| tr -d ":"`

if [ -z $card ]; then
	echo "ERROR: no recodable cards found"
	exit 1
fi
if [ $# -ge 1 ]; then
	card=${1}
fi
if [ $# -eq 3 ]; then
	julius_path_main_conf=${2}
	julius_path_amgmm_conf=${3}
fi

export ALSADEV="plughw:"${card}",0"
echo "ALSADEV =" $ALSADEV

# マイクの音量を設定したくない場合は、下記の1行を削除する
amixer -c ${card} sset Mic capture 90%

if [ $? -ne 0 ]; then
	amixer -c ${card}
	echo "ERROR: not audio card," $ALSADEV
	exit 1
fi
echo ${julius_com} "-C" ${julius_path_main_conf} "-C" ${julius_path_amgmm_conf} "-quiet"
${julius_com} -C ${julius_path_main_conf} -C ${julius_path_amgmm_conf} -quiet | ./juliusSpeechToUdp.py SUBPROCESS
echo "Done" ${0}
exit
