/*********************************************************************
本ソースリストおよびソフトウェアは、ライセンスフリーです。
著作権表示の改変は禁止します。

DHT11の簡易湿度計 for Arduino

ご注意：
・DHT11はI2Cではありません。
・3V動作につき取得エラーが発生することがあります。

                               Copyright (c) 2012-2019 Wataru KUNINO
                               https://bokunimo.net
*********************************************************************/
/*
参考文献：
・DHT 11 Humidity & Temperature Sensor(D-Robotics社HDT用 IF)
	D-Robotics	7/30/2010
・AM2302 Product Manual
	Aosong	(www.aosong.com)
・Grove - Temp&Humi Sensor [SEN11301P]	Seeed Studio Bazaar
	http://www.seeedstudio.com/depot/grove-temphumi-sensor-p-745.html
・Digital-output relative humidity & temperature sensor/module DHT22
	Aosong Electronics Co.,Ltd	http://www.humiditycn.com
*/

#define DHTport			27			// DHT_DATAポート番号
// #define SD_CS		10			// SDカードCS端子(デフォルト=10)
// #include <SD.h>
int DHTtype=11;						// AM2302時はDHT=22にする

volatile float _i2c_dht_hum = -1.0;
volatile float _i2c_dht_temp = -999.;

// DHTポートの初期化
void _DHTInit(int ms) {
	pinMode(DHTport,INPUT_PULLUP);
	for(int i=0;i<ms;i++) delay(1);	// 2秒
}

// DHT TSシーケンス
byte _DHTTSSeq(int adj) {		// adj = 起動時のACK待ち時間を調整
	byte dht11_in;
	int t=0;
	// start condition
	// 1. pull-down i/o pin from 18ms
//	digitalWrite(DHTport, LOW);
	pinMode(DHTport,OUTPUT);
	digitalWrite(DHTport, LOW);
	if(DHTtype==22) delayMicroseconds(1000 + adj * 100);
	else delay(22 + adj * 2);	//  Host start signal pull down time > 18 ms (20msでは足りなかった）
	digitalWrite(DHTport, HIGH);	// 立ち上がりを補助
	delayMicroseconds(2);			// 正常応答時は10usなので、その1/5
	pinMode(DHTport,INPUT_PULLUP);
	if(DHTtype==22)	delayMicroseconds(30+40);	// High 30us + Slave ACK 80us/2
	else 			delayMicroseconds(20+40);	// High 20us + Slave ACK 80us/2

	dht11_in = digitalRead(DHTport);	// 正常時 = LOW
	if(dht11_in){
		Serial.println("DHT start condition 1 not met");
		return 1;
	}
	delayMicroseconds(80);
	dht11_in = digitalRead(DHTport);	// 正常時 = HIGH
	if(!dht11_in){
		Serial.println("DHT start condition 2 not met");
		return 1;
	}
	while( digitalRead(DHTport) ){	// LOW待ち
		if(t>100){
			Serial.println("DHT start DHTport no Signal");
			return(1);
		}
		t++;
		delayMicroseconds(1);
	}
	return(0);
}

// DHTデータ受信
byte _read_dht11_dat(){
	byte i = 0;
	int t=0;
	byte result=0;
	noInterrupts();
	for(i=0; i< 8; i++){
		while( !digitalRead(DHTport) ){ // High待ち
			if(t>100){
				Serial.println("DHT no data");
				interrupts();
				return 0;
			}
			t++;
			delayMicroseconds(1);
		}
		t=0;
		delayMicroseconds(47);			// 23-27 or 68-74us 
		if( digitalRead(DHTport) ){
			result |=(1<<(7-i));
			while( digitalRead(DHTport) ){ // wait '1' finish
				if(t>100){
					interrupts();
					Serial.println("DHT no finish data");
					return 0;
				}
				t++;
				delayMicroseconds(1);
			}
		}
	}
	interrupts();
	return result;
}

// DHT ACK
byte _DHT_ACK(void) {
	int t=0;
	while( digitalRead(DHTport) ){
		if(t>100){
			Serial.println("DHT no ACK");
			return 0;
		}
		t++;
		delayMicroseconds(1);
	}
	delayMicroseconds(50);
	return 0;
//	pinMode(DHTport,OUTPUT);
//	digitalWrite(DHTport, HIGH);
}

boolean i2c_dht_Setup(int type){
	if(type ==11 || type ==22){
		DHTtype = type;
		_DHTInit(2000);
    	return true;
    }
    return false;
}

float i2c_dht_getTemp(){
	byte dht11_dat[5];
	byte dht11_check_sum;
	for(int t=0;t<3;t++){
		_DHTInit((t>0)*2000);
		if(_DHTTSSeq(t)) return -999.;
		for (int i=0; i<5; i++) dht11_dat[i] = _read_dht11_dat();
		if(_DHT_ACK()) return -999.;
		dht11_check_sum = dht11_dat[0]+dht11_dat[1]+dht11_dat[2]+dht11_dat[3];
		if(dht11_dat[4] == dht11_check_sum) break;
		Serial.printf("DHT checksum error %02x:%02x\r\n",dht11_dat[4],dht11_check_sum);
	}
	if(DHTtype==22){
		_i2c_dht_temp = ((float)(dht11_dat[2]&0x7F)*256.+(float)dht11_dat[3])/10;
		if( dht11_dat[2] & 0x80 ) _i2c_dht_temp *= -1;
	}else _i2c_dht_temp =  (float)dht11_dat[2];
	
	if(DHTtype==22)	_i2c_dht_hum = ((float)dht11_dat[0]*256.+(float)dht11_dat[1])/10;
	else			_i2c_dht_hum =  (float)dht11_dat[0];
	
	return _i2c_dht_temp;
}

float i2c_dht_getHum(){
    float ret;
    if(_i2c_dht_hum == -1.0 ) i2c_dht_getTemp();
    ret = _i2c_dht_hum;
    _i2c_dht_hum = -1.0;
    return ret;
}
