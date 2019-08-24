#!/bin/bash

echo "NUCLEO-F767ZI 用 MicroPython のファームウェアを作成し、書き込みます"
echo "参考文献： https://blog.boochow.com/article/459702269.html"
echo "ご注意：動作保証はありません"
echo "Crtl + C で中止します。"
sleep 10

echo
echo "gcc-arm-none-eabi をインストールします"
sleep 5
sudo apt-get install gcc-arm-none-eabi
# sudo apt-get install binutils-arm-none-eabi

echo
echo "MicroPython をインストールします"
sleep 5
cd
git clone http://github.com/micropython/micropython.git
cd micropython/
git fetch origin pull/3808/head:local-branch-name
git checkout local-branch-name
git cherry-pick 309fe39dbb14b1f715ea09c4b9de235a099c01b0
git submodule update --init
make -C mpy-cross
make -C ports/stm32 MICROPY_HW_ENABLE_ETH_RMII=1 BOARD=NUCLEO_F767ZI

echo
cd ports/stm32/build-NUCLEO_F767ZI
pwd
ls -l firmware.*

# make -C ports/stm32 MICROPY_HW_ENABLE_ETH_RMII=1 BOARD=NUCLEO_F767ZI deploy-stlink

echo
echo "dfu-util をインストールします"
sleep 5
sudo apt-get install dfu-util

echo
echo "NUCLEO-F767ZI へ MicroPython のファームウェアを書き込みます"

while true; do
	echo "「no」を入力すると終了します"
	echo -n "yes/no >"
	read yes
	if [ $yes = "no" ]; then
		break;
	fi
	dfu-util -a0 -d 0x0483:0xdf11 -D firmware.dfu
	if [ $? == 0 ]; then
		echo "書き込みを完了しました。"
		break;
	fi
	echo "失敗しました。"
	echo
	echo "再度、ファームウェアを書き込みますか？"
done

echo
echo "終了します"
echo "Done"
