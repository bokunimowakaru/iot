#!/bin/bash

PWD=`pwd`
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
echo "MicroPython をダウンロードします"
sleep 5
cd
git clone http://github.com/micropython/micropython.git
if [ $? != 0 ]; then
	cd micropython
	if [ $? != 0 ]; then
		echo "MicroPython のダウンロードに失敗しました"
		exit
	fi
else
	cd micropython/
	git fetch origin pull/3808/head:local-branch-name
	git checkout local-branch-name
	git cherry-pick 309fe39dbb14b1f715ea09c4b9de235a099c01b0
		# Thu Feb 28 15:30:48 2019 +1100
	git submodule update --init
fi

echo
echo "MicroPython をビルド(コンパイル)します"
sleep 5
make -C mpy-cross
if [ $? != 0 ]; then
	echo "mpy-cross のビルド(コンパイル)に失敗しました。"
	exit
fi

make -C ports/stm32 MICROPY_HW_ENABLE_ETH_RMII=1 BOARD=NUCLEO_F767ZI
if [ $? != 0 ]; then
	echo "ports/stm32 のビルド(コンパイル)に失敗しました。"
	exit
fi

echo
cd ports/stm32/build-NUCLEO_F767ZI
pwd
ls -l firmware.*

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

cd $PWD
echo "MicroPython用 LCDライブラリをダウンロードします"
wget https://raw.githubusercontent.com/wjdp/micropython-lcd/master/lcd.py

echo
echo "終了します"
echo "Done"
