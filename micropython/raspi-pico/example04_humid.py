# Raspberry Pi Pico + 湿度センサ SHT31 BluetoothモジュールRN4020で送信する
# Copyright (c) 2021 Wataru KUNINO

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

ble_ad_id = 'CD00'                      # BLEビーコン用ID(先頭2バイト)
sht31 = 0x44                            # 温湿度センサSHT31のI2Cアドレス

from machine import Pin,I2C             # ライブラリmachineのI2Cを組み込む
from machine import UART                # machineからUARTを組み込む
from utime import sleep                 # μtimeからsleepを組み込む

def rn4020(s = ''):                     # BLE RN4020との通信用の関数を定義
    if len(s) > 0:                      # 変数sが1文字以上あるとき
        print('>',s)                    # 内容を表示
        uart.write(s + '\n')            # コマンド送信
        sleep(0.1)                      # 0.1秒の待ち時間処理
    while uart.any() > 0:               # 受信バッファに文字があるとき
        rx = uart.readline().decode()   # 受信データを変数sに代入する
        print('<',rx.strip())           # 受信結果を表示する
        sleep(0.1)                      # 0.1秒の待ち時間処理

led = Pin(25, Pin.OUT)                  # GPIO出力用インスタンスledを生成
gnd = Pin(6, Pin.OUT)                   # GP6をSHT31のGNDピンに接続
gnd.value(0)                            # GND用に0Vを出力
vdd = Pin(3, Pin.OUT)                   # GP3をSHT31のV+ピンに接続
vdd.value(1)                            # V+用に3.3Vを出力
i2c = I2C(0, scl=Pin(5), sda=Pin(4))    # GP5をSHT31のSCL,GP4をSDAに接続

uart = UART(0, 115200, bits=8, parity=None, stop=1) # シリアルuartを生成
rn4020('V')                             # バージョン情報表示
rn4020('SF,2')                          # 全設定の初期化
sleep(0.5)                              # リセット待ち(1秒)
rn4020()                                # 応答表示
rn4020('SR,20000000')                   # 機能設定:アドバタイジング
rn4020('SS,00000001')                   # サービス設定:ユーザ定義
rn4020('SN,RN4020_HUMID')               # デバイス名:RN4020_HUMID
rn4020('R,1')                           # RN4020を再起動
sleep(3)                                # リセット後にアドバタイジング開始
rn4020('D')                             # 情報表示
rn4020('Y')                             # アドバタイジング停止

temp = 0.                               # 温度値を保持する変数tempを生成
hum  = 0.                               # 湿度値を保持する変数humを生成
payload = 0x00000000                    # 送信データを保持する変数を生成
while True:                             # 繰り返し処理
    i2c.writeto_mem(sht31,0x24,b'\x00') # SHT31にコマンド0x2400を送信する
    # i2c.writeto(sht31,b'\x24\x00')    # SHT31仕様に合わせた2バイト送信表記
    sleep(0.018)                        # SHT31の測定待ち時間
    data = i2c.readfrom_mem(sht31,0x00,6)   # SHT31から測定値6バイトを受信
    if len(data) >= 5:                  # 受信データが5バイト以上の時
        temp = float((data[0]<<8) + data[1]) / 65535. * 175. - 45.
        hum  = float((data[3]<<8) + data[4]) / 65535. * 100.
        payload = (data[1]<<24) + (data[0]<<16) + (data[4]<<8) + data[3]
    s = str(round(temp,1))              # 小数点第1位で丸めた結果を文字列に
    print('Temperature =',s)            # 温度値を表示
    s = str(round(hum,1))               # 小数点第1位で丸めた結果を文字列に
    print('Humidity =',s)               # 湿度値を表示
    s = ble_ad_id + '{:08X}'.format(payload)  # BLE送信データ(16進数に変換)
    led.value(1)                        # LEDをONにする
    rn4020('N,' + s)                    # データをブロードキャスト情報に設定
    rn4020('A,0064,00C8')               # 0.1秒間隔で0.2秒間のアドバタイズ
    sleep(0.1)                          # 0.1秒間の待ち時間処理
    rn4020('Y')                         # アドバタイジング停止
    led.value(0)                        # LEDをOFFにする
    sleep(5)                            # 5秒間の待ち時間処理
