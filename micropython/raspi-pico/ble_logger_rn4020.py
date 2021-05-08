#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger
#
# for:
#   example03_rn4020.py
#
# Rapberry Pi Pico + RN4020 が送信するビーコンを受信し
# ビーコンに含まれる、温度センサ値を表示します。
#
#                                          Copyright (c) 2019-2021 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_logger_sens_scan.py &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html
#   https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf

interval = 1.01                     # 動作間隔
savedata = True                     # ファイル保存の要否
username = 'pi'                     # ファイル保存時の所有者名

from bluepy import btle
from sys import argv
import getpass
from shutil import chown
from time import sleep
import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import datetime
import subprocess

def save(filename, data):
    try:
        fp = open(filename, mode='a')                   # 書込用ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
    fp.write(data + '\n')                               # dataをファイルへ
    fp.close()                                          # ファイルを閉じる
    chown(filename, username, username)                 # 所有者をpiユーザへ

def payval(num, bytes=1, sign=False):
    global val
    a = 0
    if num < 2 or len(val) < (num - 2 + bytes) * 2:
        print('ERROR: data length',len(val))
        return 0
    for i in range(0, bytes):
        a += (256 ** i) * int(val[(num - 2 + i) * 2 : (num - 1 + i) * 2],16)
    if sign:
        if a >= 2 ** (bytes * 8 - 1):
            a -= 2 ** (bytes * 8)
    return a

def printval(dict, name, n, unit):
    value = dict.get(name)
    if value == None:
        return
    if type(value) is not str:
        if n == 0:
            value = round(value)
        else:
            value = round(value,n)
    print('    ' + name + ' ' * (14 - len(name)) + '=', value, unit)

# MAIN
if getpass.getuser() != 'root':
    print('使用方法: sudo', argv[0])
    exit()
scanner = btle.Scanner()

rn4020mac = list()
rn4020dev = dict()

while True:
    # BLE受信処理
    try:
        devices = scanner.scan(interval)
    except Exception as e:
        print("ERROR",e)
        subprocess.call(["hciconfig", "hci0", "down"])
        sleep(5)
        subprocess.call(["hciconfig", "hci0", "up"])
        sleep(interval)
        continue
    sensors = dict()

    # 受信データについてBLEデバイス毎の処理
    for dev in devices:
        print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
        isRohmMedal = ''
        val = ''
        for (adtype, desc, value) in dev.getScanData():
            print("  %3d %s = %s" % (adtype, desc, value))  # ad_t=[{8:'Short Local Name'},{9:'Complete Local Name'}]
            # RN4020
            if adtype == 9 and value[0:6] == 'RN4020' and dev.addrType == 'public':
                isRohmMedal = value
                if dev.addr not in rn4020mac:
                    rn4020mac.append(dev.addr)
                    rn4020dev[dev.addr] = value
            if desc == 'Manufacturer':
                val = value
                if dev.addr in rn4020mac and val[0:4] == 'cd00':
                    isRohmMedal = rn4020dev[dev.addr]
            if isRohmMedal == '' or val == '':
                continue

            sensors = dict()
            print('    isRohmMedal   =',isRohmMedal)

            if isRohmMedal == 'RN4020_TEMP':
                # センサ値を辞書型変数sensorsへ代入
                sensors['ID'] = hex(payval(2,2))
                sensors['Temperature']\
                    = 27 - (3300 * (payval(4) * 256 + payval(5)) / 65535 - 706) / 1.721
                sensors['RSSI'] = dev.rssi

            if sensors:
                printval(sensors, 'ID', 0, '')
                printval(sensors, 'SEQ', 0, '')
                printval(sensors, 'Button', 0, '')
                printval(sensors, 'Temperature', 2, '℃')
                printval(sensors, 'Humidity', 2, '%')
                printval(sensors, 'Pressure', 3, 'hPa')
                printval(sensors, 'Illuminance', 1, 'lx')
                printval(sensors, 'Proximity', 0, 'count')
                if(sensors.get('Color R')):
                    print('    Color RGB     =',round(sensors['Color R']),\
                                                round(sensors['Color G']),\
                                                round(sensors['Color B']),'%')
                    print('    Color IR      =',round(sensors['Color IR']),'%')
                printval(sensors, 'Accelerometer', 3, 'g')
                printval(sensors, 'Geomagnetic', 1, 'uT')
                printval(sensors, 'Magnetic', 0, '')
                printval(sensors, 'Steps', 0, '歩')
                printval(sensors, 'Battery Level', 0, '%')
                printval(sensors, 'RSSI', 0, 'dB')
            isRohmMedal = ''

            # センサ個別値のファイルを保存
            date=datetime.datetime.today()
            if savedata:
                for sensor in sensors:
                    if (sensor.find(' ') >= 0 or len(sensor) <= 5 or sensor == 'Magnetic') and sensor != 'Color R':
                        continue
                    s = date.strftime('%Y/%m/%d %H:%M')
                    # s += ', ' + sensor
                    if sensor == 'Button':
                        s += ', ' + sensors['Button'][3]
                        s += ', ' + sensors['Button'][2]
                        s += ', ' + sensors['Button'][1]
                        s += ', ' + sensors['Button'][0]
                    else:
                        s += ', ' + str(round(sensors[sensor],3))
                    if sensor == 'Color R':
                        s += ', ' + str(round(sensors['Color R'],3))
                        s += ', ' + str(round(sensors['Color G'],3))
                        s += ', ' + str(round(sensors['Color B'],3))
                        s += ', ' + str(round(sensors['Color IR'],3))
                        sensor = 'Color'
                    if sensor == 'Accelerometer':
                        s += ', ' + str(round(sensors['Accelerometer X'],3))
                        s += ', ' + str(round(sensors['Accelerometer Y'],3))
                        s += ', ' + str(round(sensors['Accelerometer Z'],3))
                    if sensor == 'Geomagnetic':
                        s += ', ' + str(round(sensors['Geomagnetic X'],3))
                        s += ', ' + str(round(sensors['Geomagnetic Y'],3))
                        s += ', ' + str(round(sensors['Geomagnetic Z'],3))
                    # print(s, '-> ' + sensor + '.csv') 
                    save(sensor + '.csv', s)

'''
pi@raspberrypi:~/iot/micropython/raspi-pico $ sudo ./ble_logger_rn4020.py 

Device 00:1e:c0:xx:xx:xx (public), RSSI=-60 dB, Connectable=True
    1 Flags = 06
    9 Complete Local Name = RN4020_TEMP

Device 00:1e:c0:xx:xx:xx (public), RSSI=-63 dB, Connectable=False
    1 Flags = 04
  255 Manufacturer = cd0037a3
    isRohmMedal   = RN4020_TEMP
    ID            = 0xcd 
    Temperature   = 20.49 ℃
    RSSI          = -63 dB

'''
