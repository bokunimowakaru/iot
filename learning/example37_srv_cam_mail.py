#!/usr/bin/env python3
# coding: utf-8

# Example 37 IoTボタンでチャイム音＋写真撮影するカメラ付き玄関呼び鈴システム
# IoTボタンが送信するUDPを受信し、写真撮影とIoTチャイムへ鳴音指示を送信する
# 【メール送信機能つき】

# 接続図
#           [IoTボタン] ------> [本機] ------> [IoTチャイム]
#           ボタン操作            ↓             チャイム音
#                               [IoTカメラ]      ＋【メール送信機能つき】
#                               写真撮影

# 機器構成
#   本機        IoTボタンが押されたときにIoTチャイムへ鳴音指示
#   IoTボタン   example14_iot_btn.py
#   IoTチャイム example18_iot_chime_n.py
#   IoTカメラ   example36_iot_cam.py

ip_cams = ['127.0.0.1']                 ## 要設定 ##    # IoTカメラのIPアドレス
ip_chimes = ['127.0.0.1']               ## 要設定 ##    # IoTチャイム,IPアドレス

MAIL_ID   = '************@gmail.com'    ## 要変更 ##    # GMailのアカウント
MAIL_PASS = '************'              ## 要変更 ##    # パスワード
MAILTO    = 'watt@bokunimo.net'         ## 要変更 ##    # メールの宛先

import socket                                           # IP通信用モジュール
import urllib.request                                   # HTTP通信ライブラリ
import datetime                                         # 日時・時刻用ライブラリ
import smtplib                                          # メール送信用ライブラリ
from email.mime.multipart import MIMEMultipart          # メール形式ライブラリ
from email.mime.text import MIMEText                    # 　同・テキスト用
from email.mime.application import MIMEApplication      # 　同・添付用

def chime(ip):                                          # IoTチャイム
    url_s = 'http://' + ip                              # アクセス先をurl_sへ
    try:
        res = urllib.request.urlopen(url_s)             # IoTチャイムへ鳴音指示
    except urllib.error.URLError:                       # 例外処理発生時
        url_s = 'http://' + ip + ':8080'                # ポートを8080に変更
        try:
            urllib.request.urlopen(url_s)               # 再アクセス
        except urllib.error.URLError:                   # 例外処理発生時
            print('URLError :',url_s)                   # エラー表示

def cam(ip):                                            # IoTカメラ
    url_s = 'http://' + ip                              # アクセス先をurl_sへ
    s = '/cam.jpg'                                      # 文字列変数sにクエリを
    try:
        res = urllib.request.urlopen(url_s + s)         # IoTカメラで撮影を実行
        if res.headers['content-type'].lower().find('image/jpeg') < 0:
            res = None                                  # JPEGで無いときにNone
    except urllib.error.URLError:                       # 例外処理発生時
        res = None                                      # エラー時にNoneを代入
    if res is None:                                     # resがNoneのとき
        url_s = 'http://' + ip + ':8080'                # ポートを8080に変更
        try:
            res = urllib.request.urlopen(url_s + s)     # 再アクセス
            if res.headers['content-type'].lower().find('image/jpeg') < 0:
                res = None                              # JPEGで無いときにNone
        except urllib.error.URLError:                   # 例外処理発生時
            res = None                                  # エラー時にNoneを代入
    if res is None:                                     # resがNoneのとき
            print('URLError :',url_s)                   # エラー表示
            return None                                 # 関数を終了する
    data = res.read()                                   # コンテンツ(JPEG)を読む
    date = datetime.datetime.today().strftime('%d%H%M') # 12日18時20分 → 121820
    filename = 'cam_' + ip[-1] + '_' + date + '.jpg'    # ファイル名の作成
    try:
        fp = open(filename, 'wb')                       # 保存用ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
        return None                                     # 関数を終了する
    fp.write(data)                                      # 写真ファイルを保存する
    fp.close()                                          # ファイルを閉じる
    print('filename =',filename)                        # 保存ファイルを表示する
    return filename                                     # ファイル名を応答する

def mail(att, subject, text, files):                    # メール送信用関数
    try:
        mime = MIMEMultipart()                          # MIME形式のインスタンス
        mime['From'] = MAIL_ID                          # 送信者を代入
        mime['To'] = att                                # 宛先を代入
        mime['Subject'] = subject                       # 件名を代入
        txt = MIMEText(text.encode(), 'plain', 'utf-8') # TEXTをMIME形式に変換
        mime.attach(txt)                                # テキストを添付
        for file in files:                              # 添付ファイル(複数)
            fp = open(file, "rb")                       # ファイルを開く
            app = MIMEApplication(fp.read(),Name=file)  # ファイルをappへ代入
            fp.close()                                  # ファイルを閉じる
            mime.attach(app)                            # 保持したappを添付
        smtp = smtplib.SMTP('smtp.gmail.com', 587)      # SMTPインスタンス生成
        smtp.starttls()                                 # SSL/TSL暗号化を設定
        smtp.login(MAIL_ID, MAIL_PASS)                  # SMTPサーバへログイン
        smtp.sendmail(MAIL_ID, att, mime.as_string())   # SMTPメール送信
        smtp.close()                                    # 送信終了
        print('Mail:', att, subject, text)              # メールの内容を表示
    except Exception as e:                              # 例外処理発生時
        print('ERROR, Mail:',e)                         # エラー内容を表示
    #   raise e                                         # Exceptionを応答する

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
        for ip in ip_chimes:                            # 各機器のIPアドレスをip
            chime(ip)                                   # IoTチャイムを鳴らす
        files = []                                      # 写真のファイル
        for ip in ip_cams:                              # 各機器のIPアドレスをip
            files.append(cam(ip))                       # IoTカメラで撮影する
        msg = 'ボタンが押されました'                    # メール本文
        mail(MAILTO, 'カメラ画像', msg, files)          # 添付メールを送信する
