#!/bin/bash

echo "ESP32へ書き込みます (usage: ${0} port)"
if [ ${#} -ne 1 ]; then
	cat README.md
	echo "ERROR: シリアルポートのデバイスPath(/dev/ttyUSB*)を入力してください"
	exit
fi
if [ ! -e ${1} ]; then
	cat README.md
	echo "ERROR: 有効なデバイスPath(/dev/ttyUSB*)を入力してください"
	exit
fi
./esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size detect 0xe000 boot_app0.bin 0x1000 bootloader_qio_80m.bin 0x10000 iot-sensor-core-esp32.ino.bin 0x8000 iot-sensor-core-esp32.ino.partitions.bin
echo "Done"
