# AWS Lambda Python3.7用
# coding: utf-8

########################################################################
# lambda_rest_to_db.py
# 外部からHTTPを使って、AWSクラウド上のデータベースDynamoDBにセンサ値を
# 保持し、また保持したセンサ値を読み取ります。
#
#                                       Copyright (c) 2019 Wataru KUNINO
########################################################################

# 使用準備
# ・予め API Gateway、Dynamo DBと接続しておく（ロール設定）
# ・データベースDynamo DBにテーブルsensorsと項目deviceを作成しておく
# 
# クラウド上のデータベースからデータを受信する
# https://xxx.execute-api.xxx.amazonaws.com/sensor?device=temp._2
# {"statusCode": 200, "body": [{"value": "25", "device": "temp._2"}]}
#
# クラウド上のデータベースにデータを書き込む
# https://xxx.execute-api.xxx.amazonaws.com/sensor?device=temp._2&value=20
# {"statusCode": 200, "body": [{"value": "20", "device": "temp._2"}]} 

import json
import boto3                                        # AWS用のライブラリ
from boto3.dynamodb.conditions import Key           # データベース用

# データベース選択
db = boto3.resource('dynamodb')                     # DynamoDBの生成
dbTable = db.Table('sensors')                       # DBテーブルを指定

# 応答値
err={'statusCode':500,'body':'Internal server error'}   # 内部エラー用
ok ={'statusCode':200,'body':'Ok'}                      # 応答用

def lambda_handler(event, context):                 # Lambda関数の開始
    print('Received event:',json.dumps(event))      # 受信eventを表示
    params = event.get('params',{})                 # パラメータを取得
    query  = params.get('querystring',{})           # HTTPクエリを取得
    device = query.get('device')                    # クエリ内デバイス名
    value  = query.get('value')                     # クエリ内のセンサ値
    if value is not None:                           # センサ値の存在時
        try:                                        # DBへ値を書き込む
            dbTable.put_item(Item={'device': device , 'value': value})
        except Exception as e:
            print(e)
            return err
    try:                                            # DBから値を読み込む
        dbVals = dbTable.query(
            KeyConditionExpression = Key('device').eq(device)
        )
        print('dbVals:',dbVals['Items'])            # DBの取得値を表示
    except Exception as e:
        print(e)
        return err
    ok['body'] = dbVals['Items']                    # DB取得結果を代入
    return ok                                       # 結果を応答(外部へ)
