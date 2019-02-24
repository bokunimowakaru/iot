// スリープ中のGPIO出力設定

#include "driver/rtc_io.h"

void rtc_io_setPin(int pin,int out){
	rtc_gpio_init((gpio_num_t)pin);
	rtc_gpio_set_direction((gpio_num_t)pin,RTC_GPIO_MODE_OUTPUT_ONLY);
	rtc_gpio_set_level((gpio_num_t)pin,out);
}

esp_err_t rtc_io_on(){
	return esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_ON);
						// RTC IO, sensors and ULP co-processor
}

esp_err_t rtc_io_off(){
	return esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
}

esp_err_t rtc_io_auto(){
	return esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_AUTO);
}
