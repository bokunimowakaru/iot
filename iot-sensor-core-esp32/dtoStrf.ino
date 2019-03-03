String dtoStrf(double val,int frac){
	float delta = 0.5;
	if( (int)delta == 1 ) delta = 0.0;	// 四捨五入が行われないことを確認
	
	if( frac < 1 ){
		if(val < 0) return String((int)(val-delta));
		else        return String((int)(val+delta));
	}
	if( frac > 8 ) frac = 8;
	
	if( val < 0 ) val -= delta * pow(0.1, frac);
	else          val += delta * pow(0.1, frac);
	
	String Str = String((int)val) + ".";
	if( val < 0 ) val *= -1;
	for(int i=1;i<=frac;i++){
		val *= 10;
		Str += String( ((int)val) % 10);
	}
	
	return Str;
}

String dtoStrf(double val){
	return dtoStrf(val, 3);
}

/* TEST用
void dtoStrf_test(){
	float delta = 0.5;
	if( (int)delta == 1 ) delta = 0.0;
	Serial.println("delta(0.5)=" + dtoStrf(delta));
	
	double a=1.5;
	Serial.println("a=1.5");
	Serial.println("dtoStrf(a,0)=" + dtoStrf(a,0));
	Serial.println("dtoStrf(a,1)=" + dtoStrf(a,1));
	Serial.println("dtoStrf(a,2)=" + dtoStrf(a,2));
	Serial.println("dtoStrf(a,3)=" + dtoStrf(a,3));
	Serial.println("dtoStrf(a,8)=" + dtoStrf(a,8));
	
	a=-1.5;
	Serial.println("a=-1.5");
	Serial.println("dtoStrf(a,0)=" + dtoStrf(a,0));
	Serial.println("dtoStrf(a,1)=" + dtoStrf(a,1));
	Serial.println("dtoStrf(a,2)=" + dtoStrf(a,2));
	Serial.println("dtoStrf(a,3)=" + dtoStrf(a,3));
	Serial.println("dtoStrf(a,8)=" + dtoStrf(a,8));
	
	a=123.456789;
	Serial.println("a=123.456789");
	Serial.println("dtoStrf(a,0)=" + dtoStrf(a,0));
	Serial.println("dtoStrf(a,1)=" + dtoStrf(a,1));
	Serial.println("dtoStrf(a,2)=" + dtoStrf(a,2));
	Serial.println("dtoStrf(a,3)=" + dtoStrf(a,3));
	Serial.println("dtoStrf(a,8)=" + dtoStrf(a,8));
	
	a=-123.456789;
	Serial.println("a=-123.456789");
	Serial.println("dtoStrf(a,0)=" + dtoStrf(a,0));
	Serial.println("dtoStrf(a,1)=" + dtoStrf(a,1));
	Serial.println("dtoStrf(a,2)=" + dtoStrf(a,2));
	Serial.println("dtoStrf(a,3)=" + dtoStrf(a,3));
	Serial.println("dtoStrf(a,8)=" + dtoStrf(a,8));
}
*/
