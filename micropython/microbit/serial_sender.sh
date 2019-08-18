#!/bin/bash

# Raspberry Pi用
# micro:bitのシリアルを送信する

if [ ${#} = 0 ]; then
	data="Hello!"
else
	data=${1}
fi
stty -F /dev/ttyACM0 sane igncr -echo 115200
echo $data > /dev/ttyACM0
# timeout 1 cat /dev/ttyACM0
