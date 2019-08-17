#!/bin/bash

# Raspberry Pi用
# micro:bitのシリアルを送信する

stty -F /dev/ttyACM0 sane igncr -echo 115200
echo $1 > /dev/ttyACM0
# timeout 1 cat /dev/ttyACM0
