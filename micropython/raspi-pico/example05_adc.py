# Raspberry Pi Pico + ADC BluetoothモジュールRN4020で送信する
# Copyright (c) 2023 Wataru KUNINO

# ADCピン接続図
##############
# ADC  #Pico #
##############
# AGND # 33  #
# ADC1 # 32  #
##############

ble_ad_id = 'CD00'                      # BLEビーコン用ID(先頭2バイト)

from machine import Pin,ADC             # ライブラリmachineのADCを組み込む
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
adc1 = ADC(1)                           # ADCポート1(Pin32)用adc1を生成

uart = UART(0, 115200, bits=8, parity=None, stop=1) # シリアルuartを生成
rn4020('V')                             # バージョン情報表示
rn4020('SF,2')                          # 全設定の初期化
sleep(0.5)                              # リセット待ち(1秒)
rn4020()                                # 応答表示
rn4020('SR,20000000')                   # 機能設定:アドバタイジング
rn4020('SS,00000001')                   # サービス設定:ユーザ定義
rn4020('SN,RN4020_ADC')                 # デバイス名:RN4020_ADC
rn4020('R,1')                           # RN4020を再起動
sleep(3)                                # リセット後にアドバタイジング開始
rn4020('D')                             # 情報表示
rn4020('Y')                             # アドバタイジング停止

payload = 0x0000                        # 送信データを保持する変数を生成
while True:                             # 繰り返し処理
    adc = adc1.read_u16()               # ADC値を取得
    volt = adc * 3.3 / 65535
    payload =  ((adc & 0xff) << 8) + (adc >> 8)
    s = str(round(volt,1))              # 小数点第1位で丸めた結果を文字列に
    print('Voltage =',s)                # 電圧値を表示
    s = ble_ad_id + '{:04X}'.format(payload)  # BLE送信データ(16進数に変換)
    led.value(1)                        # LEDをONにする
    rn4020('N,' + s)                    # データをブロードキャスト情報に設定
    rn4020('A,0064,00C8')               # 0.1秒間隔で0.2秒間のアドバタイズ
    sleep(0.1)                          # 0.1秒間の待ち時間処理
    rn4020('Y')                         # アドバタイジング停止
    led.value(0)                        # LEDをOFFにする
    sleep(5)                            # 5秒間の待ち時間処理
