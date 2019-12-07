/*******************************************************************************
I2C 温湿度センサ aosong AM2320

I2C接続のセンサから測定値を取得する
aosong AM2320

本ソースリストおよびソフトウェアは、CRC演算部を除き、ライセンスフリーです。
利用、編集、再配布等が自由に行えますが、著作権表示の改変は禁止します。
(詳細は別記)

※ CRC演算部はASONG社のAM2320 Product Manualに記載のコードを転用しています。
　　該当関数：i2c_am2320_crc16

                                        Copyright (c) 2014-2019 Wataru KUNINO
                                        https://bokunimo.net/
*******************************************************************************/
/*                                        
参考資料 ASONG Digital Temperature and Humidity Sensor AM2320 Product Manual
*/

#include <Wire.h> 

/* 温湿度センサ AM2320 I2Cアドレス 0xB8(8bit) -> 0x5C(7bit) */
#define I2C_am2320 0x5C

volatile float _i2c_am2320_hum = -1.0;
volatile float _i2c_am2320_temp = -999.0;

// typedef unsigned char byte; 
// int16_t temp,hum=-1;

uint16_t i2c_am2320_crc16(unsigned char *ptr, unsigned char len){
	unsigned short crc =0xFFFF;
	unsigned char i;
	while(len--){
		crc ^=*ptr++;
		for(i=0;i<8;i++){
			if(crc & 0x01){
				crc>>=1;
				crc^=0xA001;
			}else{
				crc>>=1;
			}
		}
	}
	return crc;
}

float i2c_am2320_getTemp(){
    byte data[8],i;
    _i2c_am2320_hum = -999;
    _i2c_am2320_temp = -999;
    
    for(i=0; i<8; i++){
        Wire.beginTransmission(I2C_am2320);
    //  delay(20);
        if(Wire.endTransmission()==0) break;
        if(i==7){
            Serial.println("no response from am2320");
            return -999.;
        }
        delay(15 * (1<<i));
    }
    
//  Serial.println("endTransmission null");
    delay(5);
    Wire.beginTransmission(I2C_am2320);
//  Serial.println("beginTransmission");
    Wire.write(0x03);
    Wire.write(0x00);
    Wire.write(0x04);
    if(Wire.endTransmission()) return -999.;
    delay(1);
//  Serial.println("endTransmission config");
    Wire.requestFrom(I2C_am2320,8);
    for(i=0;i<8;i++){
        if(Wire.available()==0) return -999.;
        data[i]=Wire.read();
    }
    delay(1);
//  Serial.println("requestFrom");
    
    /*
    byte config[3];
    
    i2c_write(i2c_address,config,0);    // 起動コマンド
    delay(15);                          // 起動待ち
    config[0]=0x03;                     // readコマンド
    config[1]=0x00;                     // 開始アドレス
    config[2]=0x04;                     // データ長
    i2c_write(i2c_address,config,3);    // レジスタ 0x03設定
    delay(15);                          // 測定待ち15ms
    i2c_read(i2c_address,data,6);       // 読み出し
    */
    _i2c_am2320_temp = (float)((((int16_t)data[4])<<8)+((int16_t)data[5])) / 10.;
    _i2c_am2320_hum  = (float)((((int16_t)data[2])<<8)+((int16_t)data[3])) / 10.;
    
    if( (((uint16_t)data[7])<<8) + (uint16_t)data[6] != i2c_am2320_crc16(data,6)){
		Serial.println("CRC Error, am2320");
		return -999.;
	}
    return _i2c_am2320_temp;
}

float i2c_am2320_getHum(){
    if(_i2c_am2320_hum == -1.0 ) i2c_am2320_getTemp();
    return _i2c_am2320_hum;
}

boolean i2c_am2320_Setup(int PIN_SDA = 27, int PIN_SCL = 12);

boolean i2c_am2320_Setup(int PIN_SDA, int PIN_SCL){
//  Serial.println("i2c_am2320_Setup");
    delay(2);                   // 1ms以上
    boolean ret = Wire.begin(PIN_SDA,PIN_SCL); // I2Cインタフェースの使用を開始
    delay(18);                  // 15ms以上
    return ret;
}


/*
int main(void){
    i2c_init();
    printf("%3.1f ",(float)i2c_temp());
    printf("%3.1f\n",(float)i2c_hum());
    i2c_close();
    return 0;
}
*/
