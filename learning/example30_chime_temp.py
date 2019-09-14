#!/usr/bin/env python3
# coding: utf-8

# Example 30 IoT温度センサで熱中症予防システム
# IoT温度センサが送信する温度値情報を受信し、温度に応じたチャイム音を鳴らす

# 接続図
#           [IoT温度センサ] ------> [本機]
#               温度値              チャイム音

# 機器構成
#   本機            GPIOポート4にブザー
#   IoT温度センサ   example15_iot_temp.py

port = 4                                        # GPIO ポート番号
ping_f = 587                                    # チャイム音の周波数1
pong_f = 699                                    # チャイム音の周波数2
sensors = ['temp.','temp0','humid','press','envir'] # 対応センサのデバイス名
temp_lv = [ 28 , 30 , 32 ]                      # 警告レベル 3段階

import socket                                   # IP通信用モジュールの組み込み
from RPi import GPIO                            # GPIOモジュールの取得
from time import sleep                          # スリープ実行モジュールの取得
import threading                                # スレッド用ライブラリの取得

def chime(level):                                       # チャイム（スレッド用）
    if level <= 0 or level > 3:                         # 範囲外の値の時に
        return                                          # 何もせずに戻る
    global pwm                                          # グローバル変数pwm取得
    if level >= 1:                                      # 警告レベル1以上のとき
        pwm.ChangeFrequency(ping_f)                     # PWM周波数の変更
        pwm.start(50)                                   # PWM出力を開始。50％
        sleep(0.1)                                      # 0.1秒の待ち時間処理
        pwm.stop()                                      # PWM出力停止取得
    if level >= 2:                                      # 警告レベル2以上のとき
        pwm.ChangeFrequency(pong_f)                     # PWM周波数の変更
        pwm.start(50)                                   # PWM出力を開始。50％
        sleep(0.2)                                      # 0.2秒の待ち時間処理
        pwm.stop()                                      # PWM出力停止
    if level >= 3:                                      # 警告レベル3のとき
        for i in range(23):                             # 下記を23回繰り返す
            sleep(0.1)                                  # 0.1秒の待ち時間処理
            chime(2)                                    # レベル2と同じ鳴音処理

def check_dev_name(s):                                  # デバイス名を取得
    if not s.isprintable():                             # 表示可能な文字列で無い
        return None                                     # Noneを応答
    if len(s) != 7 or s[5] != '_':                      # フォーマットが不一致
        return None                                     # Noneを応答
    for sensor in sensors:                              # デバイスリスト内
        if s[0:5] == sensor:                            # センサ名が一致したとき
            return s                                    # デバイス名を応答
    return None                                         # Noneを応答

def get_val(s):                                         # データを数値に変換
    s = s.replace(' ','')                               # 空白文字を削除
    if s.replace('.','').replace('-','').isnumeric():   # 文字列が数値を示す
        return float(s)                                 # 小数値を応答
    return None                                         # Noneを応答

GPIO.setmode(GPIO.BCM)                          # ポート番号の指定方法の設定
GPIO.setup(port, GPIO.OUT)                      # ポート番号portのGPIOを出力に
pwm = GPIO.PWM(port, ping_f)                    # PWM出力用のインスタンスを生成

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while sock:                                             # 永遠に繰り返す
    try:
        udp, udp_from = sock.recvfrom(64)               # UDPパケットを取得
    except KeyboardInterrupt:                           # キー割り込み発生時
        print('\nKeyboardInterrupt')                    # キーボード割り込み表示
        GPIO.cleanup(port)                              # GPIOを未使用状態に戻す
        exit()                                          # プログラムの終了
    vals = udp.decode().strip().split(',')              # 「,」で分割
    dev = check_dev_name(vals[0])                       # デバイス名を取得
    if dev and len(vals) >= 2:                          # 取得成功かつ項目2以上
        val = get_val(vals[1])                          # データ1番目を取得
        level = 0                                       # 温度超過レベル用の変数
        for temp in temp_lv:                            # 警告レベルを取得
            if val >= temp:                             # 温度が警告レベルを超過
                level = temp_lv.index(temp) + 1         # レベルを代入
        print(
            'device =',vals[0],udp_from[0],\
            ', temperature =',val,\
            ', level =',level\
        )                                               # 温度取得結果を表示
        thread = threading.Thread(target=chime, args=([level])) # 関数chime
        thread.start()                                  # スレッドchimeの起動
