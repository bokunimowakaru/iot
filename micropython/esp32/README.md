# 書込み方法とライセンス

## 書込み方法  

* ESP32開発ボードをRaspberry PiのUSBへ接続してください。  

* 下記のコマンドでUSBシリアルのデバイスPath(/dev/ttyUSB*、「*」は数字)を確認してください。  
		ls -l /dev/serial/by-id/

* 下記のコマンドを入力するとESP32へ書き込むことが出来ます(/dev/ttyUSB0の数字部分を、上記で確認したUSBシリアルのデバイスPathに置き換える)。  
		cd ~/iot/micropython/esp32
		./download.sh /dev/ttyUSB0


## ライセンス MicroPython

* MicroPythonのライセンスについては、下記およびesptool_LICENSE.txtをご覧ください。  
		The MIT License (MIT)  
		Copyright (c) 2013-2019 Damien P. George  
		<https://github.com/micropython/micropython>

## ライセンス esptool.py

* esptool.pyのライセンスについては、下記およびmicropython_LICENSE.txtをご覧ください。  
		ESP8266 & ESP32 ROM Bootloader Utility  
		Copyright (C) 2014-2016 Fredrik Ahlberg, Angus Gratton, Espressif Systems (Shanghai) PTE LTD, other contributors as noted  
		<https://github.com/espressif/esptool>


## ライセンス(全般)
* ライセンスについては各ソースリストならびに各フォルダ内のファイルに記載の通りです。  
* 使用・変更・配布は可能ですが、権利表示を残してください。  
* また、提供情報や配布ソフトによって生じたいかなる被害についても，一切，補償いたしません。  
* ライセンスが明記されていないファイルについても、同様です。  
		Copyright (c) 2016-2019 Wataru KUNINO <https://bokunimo.net/>


