#!/usr/bin/env python3
# coding: utf-8

# Example 39 Raspberry Pi による見守りシステム i.myMimamoriPi
#                                         Copyright (c) 2016-2019 Wataru KUNINO
#
# テレビのリモコン信号と、IoT温度センサを監視し、指定した時間帯に4時間以上、
# テレビ操作が無かったときや、温度が高いときにメールを送信します。

# 接続図
#           [IoTボタン]----------------
#                                     ↓
#           [IoT赤外線リモコン受信]---・
#                                     ↓
#           [IoT温度センサ] ------> [本機] ------> メール送信

# 機器構成
#   本機        IoTボタンが押されたときにIoTチャイムへ鳴音指示
#   子機        IoT Sensor Coreを、以下に設定
#                   Wi-Fi設定   Wi-Fi動作モード : AP＋STA
#                               Wi-Fi STA設定   : ホームゲートウェイのSSIDとPASS
#                   センサ入力  内蔵温度センサ  : ON
#                               押しボタン      : PingPong
#                               赤外線RC        : AEHA (SHARP,Panasonic製テレビ)

# プログラムを終了させたいときは、[Ctrl] + [C]を、2回、実行する必要があります。

MAIL_ID   = '************@gmail.com'    ## 要変更 ##    # GMailのアカウント
MAIL_PASS = '************'              ## 要変更 ##    # パスワード
MAILTO    = 'watt@bokunimo.net'         ## 要変更 ##    # メールの宛先

MONITOR_START =  7  #(時)                               # 監視開始時刻
MONITOR_END   = 21  #(時)                               # 監視終了時刻
MON_INTERVAL  =  1  #(分)                               # 監視処理の実行間隔
ALLOWED_TERM  =  4  #(時間)                             # 警報指定時間(22以下)
ALLOWED_TEMP  = 35  #(℃)                               # 警報指定温度
sensors = ['temp.','temp0','humid','press','envir']     # 対応センサのデバイス名
temp_lv = [ 28 , 30 , 32 ]                              # 警告レベル 3段階

import socket                                           # IP通信用モジュール
import urllib.request                                   # HTTP通信ライブラリ
import datetime                                         # 日時・時刻用ライブラリ
import threading                                        # スレッド用ライブラリ
import smtplib                                          # メール送信用ライブラリ
from email.mime.text import MIMEText                    # メール形式ライブラリ

def mimamori(interval):
    t = threading.Timer(interval, mimamori, [interval]) # 遅延起動スレッドを生成
    t.start()                                           # (60秒後に)スレッド起動
    time_now = datetime.datetime.now()
    if time_now.hour < MONITOR_START or time_now.hour >= MONITOR_END:
        return
    global TIME_REMO, TIME_SENS
    time_remo = TIME_REMO + datetime.timedelta(hours=ALLOWED_TERM)
    time_sens = TIME_SENS + datetime.timedelta(hours=ALLOWED_TERM)
    if time_remo < time_now:                            # リモコン送信時刻を超過
        delta = time_now - TIME_REMO
        msg = 'リモコン操作が' + str(delta.hours) + '時間ありません'
        mail(MAILTO,'i.myMimamoriPi 警告',msg)
    if time_sens < time_now:                            # センサ送信時刻を超過
        delta = time_now - TIME_SENS
        msg = 'センサからの送信が' + str(delta.hours) + '時間ありません'
        mail(MAILTO,'i.myMimamoriPi 警告',msg)

def mail(att, subject, text):                           # メール送信用関数
    try:
        mime = MIMEText(text.encode(), 'plain', 'utf-8')# TEXTをMIME形式に変換
        mime['From'] = MAIL_ID                          # 送信者を代入
        mime['To'] = att                                # 宛先を代入
        mime['Subject'] = subject                       # 件名を代入
        smtp = smtplib.SMTP('smtp.gmail.com', 587)      # SMTPインスタンス生成
        smtp.starttls()                                 # SSL/TSL暗号化を設定
        smtp.login(MAIL_ID, MAIL_PASS)                  # SMTPサーバへログイン
        smtp.sendmail(MAIL_ID, att, mime.as_string())   # SMTPメール送信
        smtp.close()                                    # 送信終了
        print('Mail:', att, subject, text)              # メールの内容を表示
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示

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

TIME_REMO = datetime.datetime.now()
TIME_SENS = TIME_REMO
TIME_TEMP = TIME_REMO
mail(MAILTO,'i.myMimamoriPi','ソフトが起動しました')    # メール送信

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)# ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了
mimamori(MON_INTERVAL * 60)                             # 関数mimamoriを起動

while sock:                                             # 永遠に繰り返す
    try:
        udp, udp_from = sock.recvfrom(64)               # UDPパケットを取得
    except KeyboardInterrupt:                           # キー割り込み発生時
        print('\nKeyboardInterrupt')                    # キーボード割り込み表示
        exit()                                          # プログラムの終了
    if udp == 'Ping':                                   # 「Ping」に一致する時
        print('device = Ping',udp_from[0])              # 取得値を表示
        mail(MAILTO,'i.myMimamoriPi 通知','ボタンが押されました')
        continue                                        # whileへ戻る
    vals = udp.decode().strip().split(',')              # 「,」で分割
    dev = check_dev_name(vals[0])                       # デバイス名を取得
    if dev is None or len(vals) < 2:                            # 取得なし,又は項目1以下
        continue                                        # whileへ戻る
    val = get_val(vals[1])                              # データ1番目を取得
    level = 0                                           # 温度超過レベル用の変数
    for temp in temp_lv:                                # 警告レベルを取得
        if val >= temp:                                 # 温度が警告レベルを超過
            level = temp_lv.index(temp) + 1             # レベルを代入
    print(
        'device =',vals[0],udp_from[0],\
        ', temperature =',val,\
        ', level =',level\
    )                                                   # 温度取得結果を表示
    TIME_SENS = datetime.datetime.now()                 # センサ取得時刻を代入
    if level > 0:                                       # 警告レベル1以上のとき
        time_temp = TIME_TEMP + datetime.timedelta(minutes = 5 ** (3 - level))
        if time_temp < datetime.datetime.now():
            msg = '室温が' + str(val) + '℃になりました'
            mail(MAILTO,'i.myMimamoriPi 警告レベル=' + str(level), msg)
            TIME_TEMP = datetime.datetime.now()         # センサ取得時刻を代入

'''
実行例
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
'''
