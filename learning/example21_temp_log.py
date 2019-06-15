#!/usr/bin/env python3
# coding: utf-8
# Example 21 IoT温度計から温度値を受信し、【保存】する

filename = 'temp.csv'                                   # 温度ファイル

import socket
import datetime

def check_dev_name(s):                                  # デバイス名を取得
    if s.isprintable() and len(s) == 7 \
        and s[0:4] == 'temp' and s[5] == '_':           # IoT温度計に一致する時
        return s                                        # デバイス名を応答
    else:                                               # その他のデバイス
        return None                                     # Noneを応答

def get_val(s):                                         # データを数値に変換
    s = s.replace(' ','')                               # 空白文字を削除
    if s.replace('.','').replace('-','').isnumeric():   # 文字列が数値を示す
        return float(s)                                 # 小数値を応答
    else:                                               # 数値で無い時
        return None                                     # Noneを応答

try:
    fp = open(filename, mode='a')                       # 書込用ファイルを開く
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

try:
    while sock:                                         # 永遠に繰り返す
        udp = sock.recv(64)                             # UDPパケットを取得
        udp = udp.decode()                              # 文字列へ変換する
        udp = udp.strip()                               # 先頭末尾の改行削除
        if not udp.isprintable():                       # 表示不可能文字を含む
            print('ERROR: unknown data')                # エラー表示
            continue                                    # whileに戻る
        vals = udp.split(',')                           # 「,」で分割
        if len(vals) <= 1:                              # 項目数が1個以下
            print('ERROR: no values')                   # エラー表示
            continue                                    # whileに戻る
        val = get_val(vals[1])                          # データ1番目を取得
        dev = check_dev_name(vals[0])                   # デバイス名を取得
        if not dev:                                     # 取得失敗時
            continue                                    # whileに戻る
        date=datetime.datetime.today()                  # 日付を取得
        s = date.strftime('%Y/%m/%d %H:%M') + ', '      # 日付を変数sへ代入
        s += udp                                        # 受信データを追加
        fp.write(s + '\n')                              # 受信結果をファイルへ
        print(s, end='')                                # 受信データを表示出力
        print(', temperature =',val, end='')            # 取得値を表示
        print(' -> ' + filename, flush=True)            # ファイル名を表示

except KeyboardInterrupt:                               # キー割り込み発生時
    print('\nKeyboardInterrupt')                        # キーボード割り込み表示
    sock.close()                                        # ソケットの終了
    fp.close()                                          # ファイルを閉じる
    exit()                                              # プログラムの終了
