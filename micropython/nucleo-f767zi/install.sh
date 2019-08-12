#!/bin/bash

echo "NUCLEO-F767ZI 用 MicroPython のファームウェアを作成します"
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
echo "バイナリを作成しました。ST-LINK等で書き込んでください。"
echo "Done"
