/*********************************************************************
本ソースリストおよびソフトウェアは、ライセンスフリーです。(詳細は別記)
利用、編集、再配布等が自由に行えますが、著作権表示の改変は禁止します。

I2C接続の加速度センサの値を読み取る
Analog Devices 社 ADXL345
                               Copyright (c) 2016-2019 Wataru KUNINO
                               https://bokunimo.net/bokunimowakaru/
*********************************************************************/

#include <Wire.h> 
#define I2C_adxl 0x1D // ADXL345 の I2C アドレス SDO=L時 0x53 へ要変更

int _i2c_adxl_getReg(byte reg){
    Wire.beginTransmission(I2C_adxl);
    Wire.write(reg);
    if( Wire.endTransmission() == 0){
        Wire.requestFrom(I2C_adxl,1);
        if(Wire.available()==0) return -2;
        return Wire.read();
    }else return -1;
}

void _i2c_adxl_setReg(byte reg,byte value){
    Wire.beginTransmission(I2C_adxl);
    Wire.write(reg);
    Wire.write(value);
    Wire.endTransmission();
}

int _i2c_adxl_getData(int reg){
    int16_t data;
    
    Wire.beginTransmission(I2C_adxl);
    Wire.write(reg);
    if( Wire.endTransmission() == 0){
        Wire.requestFrom(I2C_adxl,2);
        if(Wire.available()==0) return -99999;
        data =  Wire.read();
        if(Wire.available()==0) return -99999;
        data |= Wire.read()<<8;
    }else return -99999;
    return (int)data;
}

float i2c_adxl_getAcm(int axis){         // 0:x  1:y  2:z
    int in;
    if(axis<0 || axis>2) axis=0;
    axis = axis * 2 + 0x32;     // アドレス計算
    in = _i2c_adxl_getData(axis);
    if(in < -32768 ) return -99.;
    return in * 0.004 * 9.80665;
}

boolean i2c_adxl_Setup(int PIN_SDA=21, int PIN_SCL=22, int range=0);

boolean i2c_adxl_Setup(int PIN_SDA, int PIN_SCL, int range){
    /*
    range :0から3
        0:±2g デフォルト
        1:±4g
        2:±8g
        3:±16g
    */
    
    /* I2Cの開始 */
    Wire.begin(PIN_SDA,PIN_SCL);                           // I2Cインタフェースの使用を開始

    /* ID確認 */    
    if(_i2c_adxl_getReg(0x00) != 0xE5) return false;    // レジスタ0x00—DEVID（読出し専用）
/*
    Wire.beginTransmission(I2C_adxl);
    Wire.write(0x38);                       // レジスタ0x38—FIFO_CTL（読出し／書込み）
    Wire.write(0x00);                       // FIFO バイパス 使用しない(デフォルト)
    Wire.endTransmission();
*/

    /* 割込み禁止 */
    _i2c_adxl_setReg(0x2E,0x00);                     // レジスタ0x2E—INT_ENABLE（読出し／書込み）
    _i2c_adxl_setReg(0x2C,0b00001010);               // レジスタ0x2C—BW_RATE（読出し／書込み）
    // i2c_adxl_            | |||__|_____ Rate       1111:140uA  1110:90uA 1000:60uA
    // i2c_adxl_            | ||_________ LOW_POWER
    // i2c_adxl_            |_|__________ 0

    if(_i2c_adxl_getReg(0x2D) == 0x00){
        /* 測定レンジ設定 */
        if(range<0||range>3) range=0;
        range |= 0b00101000;
        //         ||||||||_____ Range      -> 変数 rangeから
        //         ||||||_______ Justify
        //         |||||________ FULL_RES   -> 1
        //         ||||_________ 0
        //         |||__________ INT_INVERT -> 1 (割込みピンを負論理に Lアクティブ)
        //         ||___________ SPI
        //         |____________ SELF_TEST
        _i2c_adxl_setReg(0x31,range);                // DATA_FORMAT（アドレス0x31）

        /* 割込み用のスレッシュレベルを設定 */
        _i2c_adxl_setReg(0x1D,0x08);                 // レジスタ0x1D—THRESH_TAP（読出し／書込み）
                                            // 0x01 62.5 mg/LSB
                                            // 0x08  500 mg
                                            // 0x10    1 g 重力加速度
                                            // 0xA0   10 g
                                            // 0xFF 約16 g

        /* 割込み用のスレッシュ時間値を設定 */
        _i2c_adxl_setReg(0x21,0xA0);                 // レジスタ0x1D—THRESH_TAP（読出し／書込み）
                                            // 0x01   625 us/LSB
                                            // 0x10    10 ms
                                            // 0x50    50 ms
                                            // 0xA0   100 ms
                                            // 0xFF 約160 ms

        /* 割込み用のDOUBLE_TAP無視時間値を設定 */
        _i2c_adxl_setReg(0x22,0x00);                 // レジスタ0x22—Latent（読出し／書込み）
                                            // 0x01 1.25ms/LSB
                                            // 0x10   20 ms
                                            // 0x50  100 ms
                                            // 0xA0  200 ms
                                            // 0xFF 約320 ms

        /* 割込み用のDOUBLE_TAP検出時間値を設定 */
        _i2c_adxl_setReg(0x23,0x00);                 // レジスタ0x23—Window（読出し／書込み）
                                            // 0x01 1.25ms/LSB
                                            // 0x10   20 ms
                                            // 0x50  100 ms
                                            // 0xA0  200 ms
                                            // 0xFF 約320 ms
        /* 割込み用の軸を設定 */
        _i2c_adxl_setReg(0x2A,0b00000111);           // レジスタ0x2A—TAP_AXES（読出し／書込み）
        // i2c_adxl_            |  |||||_____ Z
        // i2c_adxl_            |  ||||______ Y
        // i2c_adxl_            |  |||_______ X
        // i2c_adxl_            |  ||________ Suppress
        // i2c_adxl_            |__|_________ 0

        _i2c_adxl_setReg(0x1E,0x00);
        _i2c_adxl_setReg(0x1F,0x00);
        _i2c_adxl_setReg(0x20,0x00);
        /* 測定開始 */
        _i2c_adxl_setReg(0x2D,0b00001000);
        delay(100);
        
        /* 重力値を減算する*/
        _i2c_adxl_setReg(0x1E,(byte)((int8_t)(- i2c_adxl_getAcm(0) / 0.0156 / 9.80665)));
        _i2c_adxl_setReg(0x1F,(byte)((int8_t)(- i2c_adxl_getAcm(1) / 0.0156 / 9.80665)));
        _i2c_adxl_setReg(0x20,(byte)((int8_t)(- i2c_adxl_getAcm(2) / 0.0156 / 9.80665)));

        return true;
    }else{
        /* 測定開始 */
        _i2c_adxl_setReg(0x2D,0b00001000);           // レジスタ0x2D—POWER_CTL（読出し／書込み）
        // i2c_adxl_            ||||||||_____ Wakeup 00:Frequency 8(Hz)  11: 1(Hz)
        // i2c_adxl_            ||||||_______ Sleep
        // i2c_adxl_            |||||________ Measure
        // i2c_adxl_            ||||_________ AUTO_SLEEP
        // i2c_adxl_            |||__________ Link
        // i2c_adxl_            ||___________ 0
        // i2c_adxl_            |____________ 0

        return true;
    }
}

void i2c_adxl_adxlINT(){
    _i2c_adxl_setReg(0x2D,0x00);                     // 測定停止
    
    _i2c_adxl_setReg(0x2C,0b00011000);               // レジスタ0x2C—BW_RATE（読出し／書込み）
    //             | |||__|_____ Rate       通常時      1100:140uA  1010:140uA  1000:60uA
    //             | ||_________ LOW_POWER  LowPower時  1100:90uA   1010:50uA   1000:40uA
    //             |_|__________ 0
    
    while(_i2c_adxl_getReg(0x30)& 0b11111101 ){      // 割込みフラグの終了待ち Watermarkは除外
        i2c_adxl_getAcm(0);
        i2c_adxl_getAcm(1);
        i2c_adxl_getAcm(2);
    }
    /* 割込み開始 */
    _i2c_adxl_setReg(0x2E,0b01000000);           // レジスタ0x2E—INT_ENABLE（読出し／書込み）
    // i2c_adxl_            ||||||||_____ Overrun
    // i2c_adxl_            |||||||______ Watermark
    // i2c_adxl_            ||||||_______ FREE_FALL
    // i2c_adxl_            |||||________ Inactivity
    // i2c_adxl_            ||||_________ Activity
    // i2c_adxl_            |||__________ DOUBLE_TAP
    // i2c_adxl_            ||___________ SINGLE_TAP  -> 1
    // i2c_adxl_            |____________ DATA_READY
    _i2c_adxl_setReg(0x2D,0b00001000);           // レジスタ0x2D—POWER_CTL（読出し／書込み）
    // i2c_adxl_            ||||||||_____ Wakeup 00:Frequency 8(Hz)  11: 1(Hz)
    // i2c_adxl_            ||||||_______ Sleep
    // i2c_adxl_            |||||________ Measure
    // i2c_adxl_            ||||_________ AUTO_SLEEP
    // i2c_adxl_            |||__________ Link
    // i2c_adxl_            ||___________ 0
    // i2c_adxl_            |____________ 0
}

int i2c_adxl_End(){
    _i2c_adxl_setReg(0x2E,0x00);                     // 割込み禁止
    _i2c_adxl_setReg(0x2D,0x00);                     // 測定停止
    return 0;
}

/* デバッグ用 主要レジスタ表示 
void i2c_adxl_Stat(){
  Serial.print("0x00 DEVID       0x"); Serial.println(_i2c_adxl_getReg(0x00),HEX);
  Serial.print("0x1D THRESH_TAP  0x"); Serial.println(_i2c_adxl_getReg(0x1D),HEX);
  Serial.print("0x1E OFSX        0x"); Serial.println(_i2c_adxl_getReg(0x1E),HEX);
  Serial.print("0x1F OFSY        0x"); Serial.println(_i2c_adxl_getReg(0x1F),HEX);
  Serial.print("0x20 OFSZ        0x"); Serial.println(_i2c_adxl_getReg(0x20),HEX);
  Serial.print("0x21 DUR         0x"); Serial.println(_i2c_adxl_getReg(0x21),HEX);
  Serial.print("0x22 Latent      0x"); Serial.println(_i2c_adxl_getReg(0x22),HEX);
  Serial.print("0x23 Window      0x"); Serial.println(_i2c_adxl_getReg(0x23),HEX);
  Serial.print("0x2A TAP_AXES    0x"); Serial.println(_i2c_adxl_getReg(0x2A),HEX);
  Serial.print("0x2D POWER_CTL   0x"); Serial.println(_i2c_adxl_getReg(0x2D),HEX);
  Serial.print("0x2E INT_ENABLE  0x"); Serial.println(_i2c_adxl_getReg(0x2E),HEX);
  Serial.print("0x2F INT_MAP     0x"); Serial.println(_i2c_adxl_getReg(0x2F),HEX);
  Serial.print("0x30 INT_SOURCE  0x"); Serial.println(_i2c_adxl_getReg(0x30),HEX);
  Serial.print("0x31 DATA_FORMAT 0x"); Serial.println(_i2c_adxl_getReg(0x31),HEX);
  Serial.print("0x38 FIFO_CTL    0x"); Serial.println(_i2c_adxl_getReg(0x38),HEX);
  Serial.print("0x39 FIFO_STATUS 0x"); Serial.println(_i2c_adxl_getReg(0x39),HEX);
}
*/
