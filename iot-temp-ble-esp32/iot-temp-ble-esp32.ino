/*******************************************************************************
IoT Temp 内蔵温度センサ / Si7021温湿度センサ BLE
乾電池などで動作する IoT温度センサ or IoT温湿度センサ です。

●ESP32マイコン開発ボード単体の場合はBLE温度センサとして動作します。
　（ESP32内蔵の温度センサを使用したときの、精度は良くありません。）
●Si7021を以下のピンに接続すると、BLE温湿度センサとして動作します。
　  ESP32 IO26 <-> Si7021 VIN
　  ESP32 IO27 <-> Si7021 GND
　  ESP32 IO14 <-> Si7021 SCL
　  ESP32 IO12 <-> Si7021 SDA

                                          Copyright (c) 2016-2019 Wataru KUNINO
*******************************************************************************/
/* 
   Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleScan.cpp
   Ported to Arduino ESP32 by pcbreflux
*/

#include <WiFi.h>                           // ESP32用WiFiライブラリ
#include <BLEDevice.h>
#include <BLEServer.h>
#include "esp_sleep.h"                      // ESP32用Deep Sleep ライブラリ
#define PIN_EN 2                            // GPIO 2 にLEDを接続
#define SLEEP_P 5*1000000ul                 // スリープ時間 5秒(uint32_t)
char BLE_DEVICE[12]= "espRohmTemp";         // BLE用デバイス名

BLEAdvertising *pAdvertising;

RTC_DATA_ATTR byte SEQ_N = 0;               // 送信番号
RTC_DATA_ATTR int8_t TEMP_ADJ=0;            // 温度補正値
RTC_DATA_ATTR boolean Si7021 = false;
int wake;

void setup(){                               // 起動時に一度だけ実行する関数
    WiFi.mode(WIFI_OFF);                    // 無線LANをOFFに設定
    pinMode(26,OUTPUT); digitalWrite(26,1);
    pinMode(27,OUTPUT); digitalWrite(27,0);
    pinMode(PIN_EN,OUTPUT);                 // LEDを出力に
    digitalWrite(PIN_EN,1);                 // LEDをON
    Serial.begin(115200);                   // 動作確認のためのシリアル出力開始
    wake = TimerWakeUp_init();
    delay(10);
    if(wake < 2) Si7021 = i2c_si7021_Setup(12,14);
    else if(Si7021)       i2c_si7021_Setup(12,14);
    if(Si7021) Serial.println("IoT Humidity");    // 「IoT Humidity」をシリアル出力
    else       Serial.println("IoT Temperature"); // 「IoT Temperature」をシリアル出力
    if(Si7021) strncpy(&BLE_DEVICE[7],"Humi",4);
    else       strncpy(&BLE_DEVICE[7],"Temp",4);
    BLEDevice::init(BLE_DEVICE);            // Create the BLE Device
}

void loop() {
    float temp;                             // センサ用の浮動小数点数型変数
    float hum;                             // センサ用の浮動小数点数型変数

    if(Si7021){
        temp = i2c_si7021_getTemp();
        hum = i2c_si7021_getHum();
    }else{
        temp = temperatureRead() + (float)TEMP_ADJ - 35.;
        hum = 0.;
    }
    Serial.print("Temperature    =  ");
    Serial.print(temp,2);
    Serial.println(" [degrees Celsius]");
    if(Si7021){
        Serial.print("Humidity       =  ");
        Serial.print(hum,2);
        Serial.println(" [\%]");
    }
    // BLE Advertizing
    pAdvertising = BLEDevice::getAdvertising();
    setBleAdvData(temp,hum);
    pAdvertising->start();                  // Start advertising
    SEQ_N++;
    sleep();
}

void sleep(){
    Serial.print("BLE Advertizing");
    delay(150);                             // 送信待ち時間
    if(ESP.getChipRevision() == 0 ){  // for Revision 0
        pAdvertising->stop();
        Serial.println("\nWaiting (ESP32 R.0)");
        digitalWrite(PIN_EN,0);                 // LEDをOFF
        delay(SLEEP_P / 1000);
        digitalWrite(PIN_EN,1);                 // LEDをON
        return;
    }
    if(wake<2) for(int i=0; i<20;i++){
        delay(500);
        Serial.print('.');
    }
    digitalWrite(PIN_EN,0);                 // LEDをOFF
    pAdvertising->stop();
    btStop();
    Serial.println("\nBye!");
//  delay(200);                             // 送信待ち時間
    esp_deep_sleep(SLEEP_P);                // Deep Sleepモードへ移行
}

void setBleAdvData(float temp,float hum){
    long val;
    
    BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();
    BLEAdvertisementData oScanResponseData = BLEAdvertisementData();
    
    std::string strServiceData = "";
    strServiceData += (char)9;              // Len
    strServiceData += (char)0xFF;           // Manufacturer specific data
    strServiceData += (char)0x01;           // Company Identifier(2 Octet)
    strServiceData += (char)0x00;
    val = (long)((temp + 45.) * 374.5);
    strServiceData += (char)(val & 0xFF);   // 温度 下位バイト
    strServiceData += (char)(val >> 8);     // 温度 上位バイト
    strServiceData += (char)'\0';
    val = (long)((hum / 100) * 65536);
    strServiceData += (char)(val & 0xFF);   // 湿度 下位バイト
    strServiceData += (char)(val >> 8);     // 湿度 上位バイト
    strServiceData += (char)(SEQ_N);        // 送信番号

    oAdvertisementData.addData(strServiceData);
    oAdvertisementData.setFlags(0x06);      // LE General Discoverable Mode | BR_EDR_NOT_SUPPORTED
    oAdvertisementData.setName(BLE_DEVICE); // oAdvertisementDataは逆順に代入する
    pAdvertising->setAdvertisementData(oAdvertisementData);
    pAdvertising->setScanResponseData(oScanResponseData);

    Serial.print("data            = ");
    int len=strServiceData.size();
    if(len != (int)(strServiceData[0]) + 1 || len < 2) Serial.println("ERROR: BLE length");
    for(int i=2;i<len;i++) Serial.printf("%02x ",(char)(strServiceData[i]));
    Serial.println();
    Serial.print("data length     = 2 + 6 = ");
    Serial.printf("%d (%d)\n",len-2,22-strlen(BLE_DEVICE)-6);
}
