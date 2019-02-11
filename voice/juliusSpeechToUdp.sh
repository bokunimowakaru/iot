#!/bin/bash
# coding: utf-8

julius_path_main_conf="/home/pi/julius/dictation-kit-v4.4/main.jconf"
julius_path_amgmm_conf="/home/pi/julius/dictation-kit-v4.4/am-gmm.jconf"
julius_com="/usr/local/bin/julius"

if [ $# -eq 3 ]; then
	julius_path_main_conf=${1}
	julius_path_amgmm_conf=${2}
fi
echo ${julius_com} "-C" ${julius_path_main_conf} "-C" ${julius_path_amgmm_conf} "-quiet"
${julius_com} -C ${julius_path_main_conf} -C ${julius_path_amgmm_conf} -quiet | ./juliusSpeechToUdp.py SUBPROCESS
echo "Done" ${0}
exit
