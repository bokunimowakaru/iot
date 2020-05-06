#!/usr/bin/env python3
# coding: utf-8
# Example 06 コンピュータの体温を測って表示してみよう 【オブジェクト指向型】

class TempSensor:                                       # クラスTempSensorの定義
    _filename = '/sys/class/thermal/thermal_zone0/temp' # デバイスのファイル名
    try:                                                # 例外処理の監視を開始
        fp = open(_filename)                            # ファイルを開く
    except Exception as e:                              # 例外処理発生時
        raise Exception('SensorDeviceNotFound')         # 例外を応答

    def __init__(self):                                 # コンストラクタ作成
        self.offset = float(30.0)                       # 温度センサ補正用
        self.value = float()                            # 測定結果の保持用

    def get(self):                                      # 温度値取得用メソッド
        val = float(self.fp.read()) / 1000              # 温度センサから取得
        val -= self.offset                              # 温度を補正
        val = round(val,1)                              # 丸め演算
        self.value = val                                # 測定結果を保持
        return val                                      # 測定結果を応答

    def __del__(self):                                  # インスタンスの削除
        self.fp.close()                                 # ファイルを閉じる

def main():                                             # メイン関数
    try:                                                # 例外処理の監視を開始
        tempSensor = TempSensor()                       # 温度センサの実体化
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容の表示
        exit()                                          # プログラムの終了
    tempSensor.offset += 2.0                            # 補正値を2.0℃増やす
    tempSensor.get()                                    # 温度測定の実行
    print('Temperature =', tempSensor.value)            # 測定結果を表示する
    del tempSensor                                      # インスタンスの削除
    exit()                                              # プログラムの終了

if __name__ == "__main__":                              # プログラム実行時に
    main()                                              # メイン関数を実行
