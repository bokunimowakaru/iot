#!/bin/bash
device="/dev/ttyUSB0"
echo "ESP32へ書き込みます (usage: ${0} port)"
if [ ${#} -eq 1 ]; then
        device=${1}
fi
if [ ! -e ${device} ]; then
	cat README.md
	echo "ERROR: 有効なデバイスPath(/dev/ttyUSB*)を入力してください"
	exit
fi
if [ ! -e "../../iot-sensor-core-esp32/target/esptool.py" ]; then
	echo "esptool.pyをダウンロードしてください"
	exit
fi
../../iot-sensor-core-esp32/target/esptool.py --chip esp32 --port ${device} --baud 115200 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0xe000 ../../iot-sensor-core-esp32/target/boot_app0.bin 0x1000 ../../iot-sensor-core-esp32/target/bootloader_qio_80m.bin 0x10000 iot-temp-ble-esp32.ino.bin 0x8000 iot-temp-ble-esp32.ino.partitions.bin
echo "Done"
