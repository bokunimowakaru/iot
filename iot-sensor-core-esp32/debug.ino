boolean DEBUG_EN=false;

boolean debug_enable(int in){
	if(in == 0) DEBUG_EN=true;
	else DEBUG_EN=false;
	return false;
}

char debug_wl_status(wl_status_t in){
	char ret ='.';
	if(DEBUG_EN)Serial.print("debug_wl_status: WL_");
	switch(in){
		case WL_NO_SHIELD:
			if(DEBUG_EN)Serial.print("NO_SHIELD");
			ret ='#';
			break;
		case WL_IDLE_STATUS:
			if(DEBUG_EN)Serial.print("IDLE_STATUS");
			break;
		case WL_NO_SSID_AVAIL:
			if(DEBUG_EN)Serial.print("NO_SSID_AVAIL");
			ret ='_';
			break;
		case WL_SCAN_COMPLETED:
			if(DEBUG_EN)Serial.print("SCAN_COMPLETED");
			ret ='-';
			break;
		case WL_CONNECTED:
			if(DEBUG_EN)Serial.print("CONNECTED");
			ret ='!';
			break;
		case WL_CONNECT_FAILED:
			if(DEBUG_EN)Serial.print("CONNECT_FAILED");
			ret ='*';
			break;
		case WL_CONNECTION_LOST:
			if(DEBUG_EN)Serial.print("CONNECTION_LOST");
			ret ='*';
			break;
		case WL_DISCONNECTED:
			if(DEBUG_EN)Serial.print("DISCONNECTED");
			break;
		default:
			if(DEBUG_EN)Serial.print("UNKNOWN");
			ret ='*';
			break;
	}
	if(DEBUG_EN)Serial.println(" (" + String(in) + ")");
	return ret;
}

