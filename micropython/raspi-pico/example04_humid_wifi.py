# Raspberry Pi Pico W + 湿度センサ SHT31  [無線LAN対応版]
# Copyright (c) 2021-2023 Wataru KUNINO

# 温湿度センサ AE-SHT31 ピン接続図
##############################
#   SHT31 # Pico # GPIO
##############################
#     +V  #  5   # GP3
#    SDA  #  6   # GP4
#    SCL  #  7   # GP5
#    ADD  #  8   # GND
#    GND  #  9   # GP6
##############################

SSID = "1234ABCD"                               # 無線LANアクセスポイント SSID
PASS = "password"                               # パスワード

udp_to = '255.255.255.255'                      # UDPブロードキャスト
udp_port = 1024                                 # UDPポート番号
device_s = 'humid_3'                            # デバイス識別名
interval = 10                                   # 送信間隔（秒）

sht31 = 0x44                                    # 温湿度センサSHT31のI2Cアドレス

from machine import Pin,I2C                     # machineのI2Cを組み込む
from machine import UART                        # machineからUARTを組み込む
from utime import sleep                         # μtimeからsleepを組み込む
import network                                  # ネットワーク通信
import usocket                                  # μソケット通信

led = Pin("LED", Pin.OUT)                       # Pico W LED用ledを生成
gnd = Pin(6, Pin.OUT)                           # GP6をSHT31のGNDピンに接続
gnd.value(0)                                    # GND用に0Vを出力
vdd = Pin(3, Pin.OUT)                           # GP3をSHT31のV+ピンに接続
vdd.value(1)                                    # V+用に3.3Vを出力
i2c = I2C(0, scl=Pin(5), sda=Pin(4))            # GP5をSHT31のSCL,GP4をSDAに接続

wlan = network.WLAN(network.STA_IF)             # 無線LAN用のwlanを生成
wlan.active(True)                               # 無線LANを起動
wlan.connect(SSID, PASS)                        # 無線LANに接続
while wlan.status() != 3:                       # 接続待ち
    print('.', end='')                          # 接続中表示
    led.toggle()                                # LEDの点灯／非点灯の反転
    sleep(1)                                    # 1秒間の待ち時間処理
print('\n',wlan.ifconfig())                     # 無線LANの状態を表示

temp = 0.                                       # 温度値を保持する変数tempを生成
hum  = 0.                                       # 湿度値を保持する変数humを生成
while True:                                     # 繰り返し処理
    i2c.writeto_mem(sht31,0x24,b'\x00')         # SHT31にコマンド0x2400を送信する
    # i2c.writeto(sht31,b'\x24\x00')            # SHT31仕様に合わせた2バイト送信表記
    sleep(0.018)                                # SHT31の測定待ち時間
    data = i2c.readfrom_mem(sht31,0x00,6)       # SHT31から測定値6バイトを受信
    if len(data) >= 5:                          # 受信データが5バイト以上の時
        temp = float((data[0]<<8) + data[1]) / 65535. * 175. - 45.
        hum  = float((data[3]<<8) + data[4]) / 65535. * 100.
        payload = (data[1]<<24) + (data[0]<<16) + (data[4]<<8) + data[3]
    temp_s = str(round(temp,1))                 # 小数点第1位で丸めた結果を文字列に
    print('Temperature =',temp_s)               # 温度値を表示
    hum_s = str(round(hum,1))                   # 小数点第1位で丸めた結果を文字列に
    print('Humidity =',hum_s)                   # 湿度値を表示
    led.value(1)                                # LEDをONにする

    sock = usocket.socket(usocket.AF_INET,usocket.SOCK_DGRAM) # μソケット作成
    udp_s = device_s + ', ' + temp_s            # 表示用の文字列変数udp
    udp_s += ',' + hum_s
    print('send :', udp_s)                      # 受信データを出力
    udp_bytes = (udp_s + '\n').encode()         # バイト列に変換

    try:
        sock.sendto(udp_bytes,(udp_to,udp_port)) # UDPブロードキャスト送信
    except Exception as e:                      # 例外処理発生時
        print(e)                                # エラー内容を表示
    sock.close()                                # ソケットの切断

    led.value(0)                                # LEDをOFFにする
    sleep(interval)                             # 送信間隔用の待ち時間処理
