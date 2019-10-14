#!/usr/bin/env python3
# coding: utf-8

# メールの送信を行います。

import smtplib
from email.mime.text import MIMEText

MAIL_ID   = '************@gmail.com'    ## 要変更 ##    # GMailのアカウント
MAIL_PASS = '************'              ## 要変更 ##    # パスワード
mail_to   = 'watt@bokunimo.net'         ## 要変更 ##    # メールの宛先

def mail(att, subject, text):                           # メール送信用関数
    mime = MIMEText(text.encode(), 'plain', 'utf-8')    # TEXTをMIME形式に変換
    mime['From'] = MAIL_ID                              # 送信者を代入
    mime['To'] = att                                    # 宛先を代入
    mime['Subject'] = subject                           # 件名を代入
    smtp = smtplib.SMTP('smtp.gmail.com', 587)          # SMTPインスタンス生成
    smtp.starttls()                                     # SSL/TSL暗号化を設定
    smtp.login(MAIL_ID, MAIL_PASS)                      # SMTPサーバへログイン
    smtp.sendmail(MAIL_ID, att, mime.as_string())       # SMTPメール送信
    smtp.close()                                        # 送信終了

mail(mail_to,'Python 仮免許演習中','これは、テスト用のメールです。')
