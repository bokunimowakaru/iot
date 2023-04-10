#!/bin/bash

echo "ESP32 へ MicroPython を書き込みます (usage: ${0} port)"
if [ ${#} -ne 1 ]; then
	cat README.md
	PORT="/dev/ttyUSB0"
	echo "シリアルポート" ${PORT} "を使用します。"
else
	PORT=${1}
fi
if [ ! -e ${PORT} ]; then
	cat README.md
	echo "ERROR: 引数に有効なデバイスPath(/dev/ttyUSB*)を入力してください"
	exit
fi
if [ ! -e "./esptool.py" ]; then
	echo "esptool.pyをダウンロードします"
	wget https://raw.githubusercontent.com/espressif/esptool/master/esptool.py
	chmod a+x esptool.py
	wget https://raw.githubusercontent.com/espressif/esptool/master/LICENSE
	\mv -f LICENSE esptool_LICENSE.txt
fi

filename="esp32-20220618-v1.19.1.bin"
if [ ! -e ${filename} ]; then
	echo ${filename} "をダウンロードします"
	wget https://micropython.org/resources/firmware/${filename}
	wget https://github.com/micropython/micropython/blob/master/LICENSE
	\mv -f LICENSE micropython_LICENSE.txt
fi

echo "ESP32を初期化します。"
./esptool.py --chip esp32 --port ${PORT} erase_flash
if [ $? -ne 0 ]; then
	cat README.md
	echo "初期化に失敗しました。"
	exit
fi
echo "ESP32へ書き込みます"
./esptool.py --chip esp32 --port ${PORT} --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x1000 ${filename}
if [ $? -ne 0 ]; then
	cat README.md
	echo "書き込みに失敗しました。"
	exit
fi
echo "ESP32への書き込みが完了しました。"
echo "ライセンスesptool_LICENSE.txtとmicropython_LICENSE.txtを確認してから使用してください。"
echo "Done"
