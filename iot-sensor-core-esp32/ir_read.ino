/*********************************************************************

赤外線リモコン受信部 for Arduino Version 2.0

本ソースリストおよびソフトウェアは、ライセンスフリーです。
利用、編集、再配布等が自由に行えますが、著作権表示の改変は禁止します。

                               Copyright (c) 2009-2019 Wataru KUNINO
                               https://bokunimo.net/bokunimowakaru/
*********************************************************************/

// RTC_DATA_ATTR byte		PIN_IR_IN	= 27;		// IO 4(10番ピン) にIRセンサを接続
// RTC_DATA_ATTR byte		PIN_IR_OUT	= 2;		// GPIO 2(24番ピン)赤外線LEDの接続ポート

// #define PIN_IR_IN 4                 // IO 4(10番ピン) にIRセンサを接続
#define IR_IN_OFF		1				// 赤外線センサ非受光時の入力値
#define IR_IN_ON		0				// 赤外線センサ受光時の入力値
#define IR_SYNC_WAIT	2*16*470		// 待ち時間[us] (15ms) ※intの範囲

//enum IR_TYPE{IR_AEHA=1,IR_NEC=2,IR_SIRC=3};// 家製協IR_AEHA、IR_NEC、SONY IR_SIRC切り換え
#ifndef IR_AEHA
#define IR_AEHA		1
#define IR_NEC		2
#define IR_SIRC		3
#endif
#ifndef IR_AUTO
#define IR_AUTO		4
#endif

//	#define DEBUG
#define DEBUG_ARDUINO

/*
int micros_prev,micros_sec=0;

int micros(){
	int micros;
	gettimeofday(&micros_time, NULL);    // time(&micros_time);
	micros = micros_time.tv_usec;
	if(micros_prev > micros ) micros_sec++;
	micros_prev = micros;
	micros += micros_sec * 1000000;
	return micros;
}

void micros_0(){
	micros_sec=0;
}

byte digitalRead(){
    fgpio = fopen(gpio, "r");
    if(fgpio){
		fgets(buf, S_NUM, fgpio);
    	fclose(fgpio);
    	return (byte)atoi(buf);
    }
    return 255;
}
*/

void ir_read_init(void){
	pinMode(PIN_IR_IN, INPUT);
}

/* シンボル読取り*/
int ir_sens(byte det){
	unsigned long counter;
	byte in,det_wait,det_count;
	
	if( det == IR_IN_OFF ){		/* AEHA, NEC */
		det_wait = IR_IN_ON;		// 消灯待ち
		det_count= IR_IN_OFF;		// 消灯カウント
	}else{						/* SIRC */
		det_wait = IR_IN_OFF;		// 点灯待ち
		det_count= IR_IN_ON;		// 点灯カウント
	}
	/* 待ち */
	counter = micros()+IR_SYNC_WAIT;
	do in = digitalRead(PIN_IR_IN);
	while( micros()<counter && (in == det_wait) );
	/* カウント */
	counter = micros()+IR_SYNC_WAIT;
	if(in == det_wait) return( -1 );	/* 待ちタイムアウト */
	do in = digitalRead(PIN_IR_IN);
	while( micros()<counter && (in == det_count));
	counter = micros() - counter + IR_SYNC_WAIT;
	if( in == det_count ) return( -2 );		/* 変化せず */
	if( counter > IR_SYNC_WAIT ) return( -3 );	/* 長すぎ */
	return( (int)counter );
}

/* 赤外線信号読み取りシンプル */
int ir_read(byte *data, const byte data_num, byte mode){	// mode の constを解除
	int i,bit;
	int data_len= -1;				// Irデータのビット数
	int len, data_wait;
	int	len_on=0,len_off=0;			// 信号長(ループカウント)
	int symbol_len, noise;			// 判定用シンボル長
	byte det = IR_IN_OFF;			// 判定時の入力信号レベル(SIRC対応)
	byte in=0;
	#ifdef DEBUG
		int t[1024];
		int t_i=0;
	#endif
	
	if(data_num<2) return( -3 );			/* 入力不備 */
	/* SYNC_ON検出 */
	len_on = ir_sens(IR_IN_ON);	// 受光待ち
	if( len_on < 0 ) return( -1 );			/* タイムアウト */
	/* SYNC_OFF検出 */
	len_off = ir_sens(IR_IN_OFF);
	if( len_off < 0 ) return( -2 );			/* エラー */
	
	/* モード設定 (SIRCについては最初の1ビットに遅延が許されないので、初期の遅延を最小化する)*/
	if( mode == IR_AUTO){
		if( len_off < 1200 ){
			mode=IR_SIRC;
		}else if( len_off < 3000 ) mode = IR_AEHA; else mode = IR_NEC;
	}
	switch( mode ){
		case IR_SIRC: 					// H(4T) + L(1T)	4:1
		//	micros_0();
			for(bit=0;bit<7;bit++){
				len = ir_sens( IR_IN_ON );
				if( len > 225 && len < 1800){
					if( len < 900 ){
						in = in>>1;
						in += 0;
					}else{
						in = in>>1;
						in += 128;
					}
				}else break;
			}
			in >>= 1;
			data[0]=in;
			if(bit==7){
				bit=0;
				for(i=1;i<3;i++){
					in = 0;
					for(bit=0;bit<8;bit++){
						len = ir_sens( IR_IN_ON );
						if( len > 225 && len < 1800){
							if( len < 900 ){
								in = in>>1;
								in += 0;
							}else{
								in = in>>1;
								in += 128;
							}
						}else{
							in = in>>(8 - bit);
							data[i]=in;
							data_len = i * 8 + bit;
							i = data_num -1;	// break for i
							bit=7;				// break for bit
						}
					}
					data[i]=in;
				}
			}
			symbol_len = (3*len_off)/2;
			det=IR_IN_ON;
			break;
		case IR_NEC:						// H(16T) + L(8T)	2:1
			symbol_len = len_off/4;		// ON(1T)+OFF(3T) 判定 2T ∴ 8T -> 2T
			det=IR_IN_OFF;
			break;
		case IR_AEHA:						// H(8T) + L(4T)	2:1
		default:
			symbol_len = len_off/2;		// ON(1T)+OFF(3T) 判定 2T ∴ 4T -> 2T
			det=IR_IN_OFF;
			break;
		
	}
	if(det==IR_IN_OFF){
	//	micros_0();
		/* データー読取り*/
		data_wait = 3 * symbol_len;		// 終了検出するシンボル長
		noise = symbol_len /6;			// ノイズと判定するシンボル長
		for(i=0;i<data_num;i++){
			in = 0;
			for(bit=0;bit<8;bit++){
				len = ir_sens( IR_IN_OFF );	// ir_sens( det )
				if( len > noise && len < data_wait){
					if( len < symbol_len ){
						in = in>>1;
						in += 0;
					}else{
						in = in>>1;
						in += 128;
					}
					#ifdef DEBUG
						t[t_i]=len;
						t_i++;			// if(t_i>1023) t_i=1023;
					#endif

				}else{
					in = in>>(8 - bit);
					data[i]=in;
					data_len = i * 8 + bit;
					i = data_num -1;	// break for i
					bit=7;				// break for bit
					#ifdef DEBUG
						t[t_i]=len;
						t_i++; if(t_i>1023){
							printf("DEBUG:out of memory\n");
							goto debug_exit;
						}
					#endif
				}
			}
			data[i]=in;
		}
	}
	#ifdef DEBUG	//1234567890
		debug_exit:
		printf("------------------------ DEBUG ----------------------\n");
		printf("Mode    = %d",mode);
		switch(mode){
			case IR_AEHA: printf(" (AEHA)\n"); break; 
			case IR_NEC : printf(" (NEC )\n"); break; 
			case IR_SIRC: printf(" (SIRC)\n"); break; 
			default  : printf(" (UNKNOWN)\n"); break; 
		}
		printf("Detector= %d",det);
		if(det==IR_IN_OFF) printf(" (IR_IN_OFF)\n"); else printf(" (IR_IN_ON)\n");
		printf("SYNC LEN= %d\n",len_on+len_off);
		printf("SYNC ON = %d\n",len_on);
		printf("SYNC OFF= %d\n",len_off);
		printf("SYMOL   = %d\n",symbol_len);
		printf("DATA LEN= %d\n",data_len);
		len=data_len/8;
		if(data_len%8)len++;
		printf("data[%02d]= {%02X",len,data[0]);
		for(i=1;i<len;i++) printf(",%02X",data[i]);
		printf("}\n");
		for(i=0;i<t_i;i++){
			printf("%4d ",t[i]);
			if(i%8==7)printf("\n");
		}
		printf("\n");
	#endif // DEBUG
	#ifdef DEBUG_ARDUINO
		Serial.print("Mode    = ");Serial.print(mode);
		switch(mode){
			case IR_AEHA: Serial.print(" (AEHA)\n"); break; 
			case IR_NEC : Serial.print(" (NEC )\n"); break; 
			case IR_SIRC: Serial.print(" (SIRC)\n"); break; 
			default  : Serial.print(" (UNKNOWN)\n"); break; 
		}
		Serial.print("Detector= ");Serial.print(det);
		if(det==IR_IN_OFF) Serial.print(" (IR_IN_OFF)\n"); else Serial.print(" (IR_IN_ON)\n");
		Serial.print("SYNC LEN= ");Serial.println(len_on+len_off);
		Serial.print("SYNC ON = ");Serial.println(len_on);
		Serial.print("SYNC OFF= ");Serial.println(len_off);
		Serial.print("SYMOL   = ");Serial.println(symbol_len);
		Serial.print("DATA LEN= ");Serial.println(data_len);
		
		len=data_len/8;
		if(data_len%8)len++;
		Serial.printf("data[%02d]= {%02X",len,data[0]);
		for(i=1;i<len;i++) Serial.printf(",%02X",data[i]);
		Serial.printf("}\n");
	#endif
	/* データの有効性のチェック 共通 */
	if(data_len<16)data_len=-2;					// 2バイトに満たないのは無効
	if(data[0]==0 && data[1]==0) data_len=-3;	// メーカーコード00
	/*  有効性のチェック AEHA */
	switch( mode ){
		case IR_AEHA:
			in=(	data[0]^
					(data[0]>>4)^
					data[1]^
					(data[1]>>4)^
					data[2]
				)&0x0F;
			if( in ){
				data_len=-4;	// メーカーコードのパリティ確認
				#ifdef DEBUG
					printf("AEHA ERR= %02X ##############################\n",in);
				#endif // DEBUG
			}
			break;
		case IR_NEC:
			in=(	data[2]^
					data[3]^
					0xFF
				)&0xFF;
			if( in ){
				data_len=-5;	// データのパリティ確認
				#ifdef DEBUG
					printf("NEC  ERR= %02X ##############################\n",in);
				#endif // DEBUG
			}
			break;
		default:
			break;
	}
	return(data_len);
}

/*
Mode    = 0 (AEHA)
Detector= 1 (IR_IN_OFF)
SYNC LEN= 5356
SYNC ON = 3640
SYNC OFF= 1716
SYMOL   = 858
DATA LEN= 48
48,AA,5A,8F,12,15,E1
*/