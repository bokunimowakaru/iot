import radio
from microbit import *

radio.on()
print('Ready Accem')
display.scroll('Accem')
val = 0
while True:
	val_prev = val
	val = accelerometer.get_x()
	val = round(val / 10)
	if abs(val - val_prev) >= 3:
		tx = str(val)
		print('Tx:',tx)
		radio.send(tx)
		display.scroll(tx)
		sleep(1000)
