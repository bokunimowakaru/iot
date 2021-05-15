#!/usr/bin/env python3
# coding: utf-8

# Example 32 IoT温度センサ用・測定結果グラフ化プログラム
# 参考文献 https://matplotlib.org/

sensors = ['temp.','temp0','humid','press','envir']     # 対応センサのデバイス名

import socket                                           # IP通信用ライブラリ
import datetime                                         # 日時・時刻用ライブラリ
import matplotlib                                       # グラフ用ライブラリ
matplotlib.use('Agg')                                   # CLI利用
import matplotlib.pyplot as plt                         # Pyplotの組み込み

def plotter(time,value):                                # グラフ描画
    plt.plot(time,value,'b')                            # グラフ線を追加する
    ymin = plt.ylim()[0]                                # 現在の下限値を取得
    ymax = plt.ylim()[1]                                # 現在の上限値を取得
    if value[1] < ymin:                                 # 下限値を下回った時
        ymax = value[1] - 5 + (value[1] % 5)            # Y軸の表示範囲を拡大
    if value[1] > ymax:                                 # 上限値を超えた時
        ymax = value[1] + 5 - (value[1] % 5)            # Y軸の表示範囲を拡大
    plt.ylim(ymin, ymax)                                # Y軸の表示範囲を設定
    plt.savefig('graph.png')                            # ファイルへ保存

def check_dev_name(s):                                  # デバイス名を取得
    if s.isprintable() and len(s) == 7 and s[5] == '_': # 形式が一致する時
        for dev in sensors:                             # センサリストの照合
            if s[0:5] == dev:                           # デバイス名が一致
                return s                                # デバイス名を応答
    return None                                         # Noneを応答

def get_val(s):                                         # データを数値に変換
    s = s.replace(' ','')                               # 空白文字を削除
    try:                                                # 小数変換の例外監視
        return float(s)                                 # 小数に変換して応答
    except ValueError:                                  # 小数変換失敗時
        return None                                     # Noneを応答

print('Listening UDP port', 1024, '...', flush=True)    # ポート番号1024表示
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)    # オプション
    sock.bind(('', 1024))                               # ソケットに接続
except Exception as e:                                  # 例外処理発生時
    print(e)                                            # エラー内容を表示
    exit()                                              # プログラムの終了

plt.title('Temperature')                                # グラフのタイトル設定
plt.xlabel('time')                                      # グラフ横軸ラベル設定
plt.ylabel('Degree Celsius')                            # グラフ縦軸ラベル設定
plt.ylim(20, 30)                                        # グラフ縦軸の範囲設定
time = []                                               # 描画する時刻の保持用
value = []                                              # 描画する値の保持用
try:
    while sock:                                         # 永遠に繰り返す
        udp, udp_from = sock.recvfrom(64)               # UDPパケットを取得
        vals = udp.decode().strip().split(',')          # 「,」で分割
        num = len(vals)                                 # データ数の取得
        dev = check_dev_name(vals[0])                   # デバイス名を取得
        if dev is None or num < 2:                      # 不適合orデータなし
            continue                                    # whileに戻る
        date=datetime.datetime.today()                  # 日付を取得
        s = date.strftime('%Y/%m/%d %H:%M') + ', '      # 日付を変数sへ代入
        s += udp_from[0] + ', ' + dev                   # 送信元の情報を追加
        for i in range(1,num):                          # データ回数の繰り返し
            val = get_val(vals[i])                      # データを取得
            s += ', '                                   # 「,」を追加
            if val is not None:                         # データがある時
                s += str(val)                           # データを変数sに追加
        print(s, flush=True)                            # 受信データを表示
        time.append(date)                               # 配列変数に時刻を追加
        value.append(get_val(vals[1]))                  # 配列変数に温度値を追加
        if len(time) >= 2:                              # 配列数が2のとき
            plotter(time,value)                         # グラフ表示を実行
            del time[0]                                 # 古い保持内容を削除
            del value[0]                                # 古い保持内容を削除

except KeyboardInterrupt:                               # キー割り込み発生時
    print('\nKeyboardInterrupt')                        # キーボード割り込み表示
    sock.close()                                        # ソケットの終了
    exit()                                              # プログラムの終了
