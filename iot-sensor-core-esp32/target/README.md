# 書込み方法とライセンス

## 書込み方法  

* ESP32開発ボードをRaspberry PiのUSBへ接続してください。  

* 下記のコマンドでUSBシリアルのデバイスPath(/dev/ttyUSB*、「*」は数字)を確認してください。  
		ls -l /dev/serial/by-id/

* 下記のコマンドを入力するとESP32へ書き込むことが出来ます(/dev/ttyUSB0の数字部分を、上記で確認したUSBシリアルのデバイスPathに置き換える)。  
		cd ~/iot/iot-sensor-core-esp32/target  
		./iot-sensor-core-esp32.sh  

## ライセンス esptool.py boot_app0.bin bootloader_qio_80m.bin

* esptool.py のライセンスについては、下記およびesptool_LICENSE.txtをご覧ください。  
		ESP8266 & ESP32 ROM Bootloader Utility  
		Copyright (C) 2014-2016 Fredrik Ahlberg, Angus Gratton, Espressif Systems (Shanghai) PTE LTD, other contributors as noted  
		<https://github.com/espressif/esptool>

* boot_app0.bin bootloader_qio_80m.bin のライセンスについては、下記および esp32_LICENSE.md をご覧ください。  
		Espressif Systems (Shanghai, China) http://www.espressif.com
		<https://github.com/espressif/arduino-esp32>

## ライセンス(全般)

* ライセンスについては各ソースリストならびに各フォルダ内のファイルに記載の通りです。  
* 使用・変更・配布は可能ですが、権利表示を残してください。  
* また、提供情報や配布ソフトによって生じたいかなる被害についても，一切，補償いたしません。  
* ライセンスが明記されていないファイルについても、同様です。  

	Copyright (c) 2016-2020 Wataru KUNINO <https://bokunimo.net/>


