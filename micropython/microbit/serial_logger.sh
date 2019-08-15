#!/bin/bash
stty -F /dev/ttyACM0 sane igncr 115200
cat /dev/ttyACM0
