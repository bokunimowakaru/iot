/*********************************************************************
本ソースリストおよびソフトウェアは、ライセンスフリーです。(詳細は別記)
利用、編集、再配布等が自由に行えますが、著作権表示の改変は禁止します。

I2C接続の温湿度センサの値を読み取る
SILICON LABS社 Si7021

参考文献
https://www.silabs.com/documents/public/data-sheets/Si7021-A20.pdf

							   Copyright (c) 2017-2023 Wataru KUNINO
							   https://bokunimo.net/bokunimowakaru/
*********************************************************************/

#include <Wire.h> 
#define I2C_si7021 0x40 		   // Si7021 の I2C アドレス 

volatile float _i2c_si7021_hum = -999;
volatile float _i2c_si7021_temp = -999;

int _i2c_si7021_mode = 7021;	// 7013, 7020, 7021, HTU21=-21

float i2c_si7021_getTemp(){
	int temp,hum,i;
	if( _i2c_si7021_temp >= -100 ){
		float ret;
		ret = _i2c_si7021_temp;
		_i2c_si7021_temp = -999;
		return ret;
	}
	_i2c_si7021_hum=-999.;
	_i2c_si7021_temp = -999;
	Wire.beginTransmission(I2C_si7021);
//	Wire.write(0xF5);	// Measure Relative Humidity, No Hold Master Mode
	Wire.write(0xE5);	// Measure Relative Humidity, Hold Master Mode
	if(Wire.endTransmission()){
		Serial.println("ERROR: i2c_si7021_getTemp() Wire.write hum");
		return -999.;
	}
	
	delay(30);					// 15ms以上
	Wire.requestFrom(I2C_si7021,2);
	i = Wire.available();
	if(i<2){
		Serial.println("ERROR: i2c_si7021_getTemp() Wire.requestFrom hum");
		return -999.;
	}
	hum = Wire.read();
	hum <<= 8;
	hum += Wire.read();
	_i2c_si7021_hum = (float)hum / 65536. * 125. - 6.;
	
	delay(18);					// 15ms以上

	if(_i2c_si7021_mode >= 0){
		Wire.beginTransmission(I2C_si7021);
		Wire.write(0xE0);		// Read Temperature Value from Previous RH Measurement
		if(Wire.endTransmission()){
			Serial.println("ERROR: i2c_si7021_getTemp() Wire.write temp");
			return -999.;
		}
		
		delay(30);					// 15ms以上
		Wire.requestFrom(I2C_si7021,2);
		i = Wire.available();
		if(i<2){
			Serial.println("ERROR: i2c_si7021_getTemp() Wire.requestFrom temp");
			return -999.;
		}
	}else{
		Wire.beginTransmission(I2C_si7021);
		Wire.write(0xE3);
		if(Wire.endTransmission()){
			Serial.println("ERROR: i2c_si7021_getTemp() Wire.write for HTU21 temp ");
			return -999.;
		}
		
		delay(30);					// 15ms以上
		Wire.requestFrom(I2C_si7021,2);
		i = Wire.available();
		if(i<2){
			Serial.println("ERROR: i2c_si7021_getTemp() Wire.requestFrom for HTU21 temp");
			return -999.;
		}
	}
	temp = Wire.read();
	temp <<= 8;
	temp += Wire.read();

	return (float)temp / 65535. * 175.72 - 46.85;
}

float i2c_si7021_getHum(){
	float ret;
	if( _i2c_si7021_hum < 0) _i2c_si7021_temp = i2c_si7021_getTemp();
	ret = _i2c_si7021_hum;
	_i2c_si7021_hum = -999;
	return ret;
}

boolean i2c_si7021_Setup(int PIN_SDA = 21, int PIN_SCL = 22);

boolean i2c_si7021_Setup(int PIN_SDA, int PIN_SCL){
	delay(2);					// 1ms以上
	boolean ret = Wire.begin(PIN_SDA,PIN_SCL); // I2Cインタフェースの使用を開始
	if(!ret) Serial.println("ERROR: i2c_si7021_Setup Wire.begin");
	delay(35);					// 15ms以上
	if(ret){
		Wire.beginTransmission(I2C_si7021);
		Wire.write(0xE6);
		Wire.write(0x3A);
		ret = (Wire.endTransmission() == 0);
		if(!ret) Serial.println("ERROR: i2c_si7021_Setup Wire.endTransmission");
		delay(18);					// 15ms以上

		// Read Electronic ID 2nd Byte (0xFC 0xC9)
		Wire.beginTransmission(I2C_si7021);
		Wire.write(0xFC);
		Wire.write(0xC9);
		Wire.endTransmission();
		delay(18);					// 15ms以上
		Wire.requestFrom(I2C_si7021,6);
		if(Wire.available()>=6){
			uint32_t id = Wire.read();
			id <<= 8;
			id += Wire.read();
			id <<= 8;
			Wire.read(); // CRC 読み捨て
			id += Wire.read();
			id <<= 8;
			id += Wire.read();
			Wire.read(); // CRC 読み捨て
			// 0x0D=13=Si7013
			// 0x14=20=Si7020
			// 0x15=21=Si7021
			if(id>>24 ==0x0D){
				_i2c_si7021_mode = 7013;
			}else if(id>>24 ==0x14){
				_i2c_si7021_mode = 7020;
			}else if(id>>24 ==0x15){
				_i2c_si7021_mode = 7021;
			}else if(id>>24 ==0x32){
				_i2c_si7021_mode = -21;
			}else Serial.println("WARINIG: Unknown Device");
		}
		delay(18);					// 15ms以上
	}
	return ret;
}
