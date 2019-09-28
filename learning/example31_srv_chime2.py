#!/usr/bin/env python3
# coding: utf-8

# Example 29 IoTボタンや温度センサでチャイム音・玄関呼び鈴システム
# IoTボタンやIoT温度センサが送信するUDPを受信し、IoTチャイムへ鳴音指示を送信する

# 接続図
#           [IoTボタン] --+---> [本機] ------> [IoTチャイム]
#           ボタン操作    |                      チャイム音
#                         |
#       [IoT温度センサ] --+
#           温度値

# 機器構成
#   本機            IoTボタンが押されたときにIoTチャイムへ鳴音指示
#   IoTボタン       example14_iot_btn.py
#   IoT温度センサ   example15_iot_temp.py
#   IoTチャイム     example18_iot_chime_nn.py

ip_chime = '127.0.0.1'                                  # IoTチャイムのアドレス
sensors = ['temp.','temp0','humid','press','envir']     # 対応センサ名
temp_lv = [ 28 , 30 , 32 ]                              # 警告レベル 3段階
url_s = 'http://' + ip_chime                            # アクセス先

import socket                                           # IP通信用モジュール
import urllib.request                                   # HTTP通信ライブラリ
import threading                                        # スレッド用ライブラ

def chime(level):                                       # チャイム（スレッド用）
    if level is None or level < 0 or level > 3:         # 範囲外の値の時に
        return                                          # 何もせずに戻る
    global url_s                                        # グローバル変数の取得
    url_b_s = url_s + '/?B=' + str(level)               # レベルの設定
    try:
        urllib.request.urlopen(url_b_s)                 # IoTチャイムへ鳴音指示
    except urllib.error.URLError:                       # 例外処理発生時
        print('URLError :',url_s)                       # エラー表示
        # ポート8080へのアクセス用 (下記の5行)
        url_s = 'http://' + ip_chime + ':8080'          # ポートを8080に変更
        url_b_s = url_s + '/?B=' + str(level)           # レベルの設定
        try:
           urllib.request.urlopen(url_b_s)              # 再アクセス
        except urllib.error.URLError:                   # 例外処理発生時
           url_s = 'http://' + ip_chime                 # ポートを戻す

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

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

while sock:                                             # 永遠に繰り返す
    udp, udp_from = sock.recvfrom(64)                   # UDPパケットを取得
    udp = udp.decode().strip()                          # データを文字列へ変換
    if udp == 'Ping':                                   # 「Ping」に一致する時
        print('device = Ping',udp_from[0])              # 取得値を表示
        thread = threading.Thread(target=chime, args=([0]))     # 関数chime
        thread.start()                                  # スレッドchimeの起動
        continue                                        # whileへ戻る
    vals = udp.split(',')                               # 「,」で分割
    dev = check_dev_name(vals[0])                       # デバイス名を取得
    if dev and len(vals) >= 2:                          # 取得成功かつ項目2以上
        val = get_val(vals[1])                          # データ1番目を取得
        level = -1                                      # 温度超過レベル用の変数
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
