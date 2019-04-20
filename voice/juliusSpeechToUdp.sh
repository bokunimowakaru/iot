#!/bin/bash
# coding: utf-8

julius_path_main_conf="/home/pi/julius/dictation-kit-v4.4/main.jconf"
julius_path_amgmm_conf="/home/pi/julius/dictation-kit-v4.4/am-gmm.jconf"
julius_com="/usr/local/bin/julius"
export ALSADEV="plughw:0,0"

if [ $# -eq 1 ]; then
	export ALSADEV="plughw:"${1}",0"
elif [ $# -eq 3 ]; then
	export ALSADEV="plughw:"${1}",0"
	julius_path_main_conf=${2}
	julius_path_amgmm_conf=${3}
fi
echo "ALSADEV =" $ALSADEV
echo ${julius_com} "-C" ${julius_path_main_conf} "-C" ${julius_path_amgmm_conf} "-quiet"
${julius_com} -C ${julius_path_main_conf} -C ${julius_path_amgmm_conf} -quiet | ./juliusSpeechToUdp.py SUBPROCESS
echo "Done" ${0}
exit
