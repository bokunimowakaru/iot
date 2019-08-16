#!/bin/bash

# Raspberry Pi用
# micro:bitのシリアルを受信する

stty -F /dev/ttyACM0 sane igncr 115200
cat /dev/ttyACM0
