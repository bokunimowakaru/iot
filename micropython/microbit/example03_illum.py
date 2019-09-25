import radio
from microbit import *

radio.on()
print('Ready illum')
display.scroll('illum')
val = 0
while True:
	val_prev = val
	val = display.read_light_level()
	if abs(val - val_prev) >= 5:
		tx = str(val)
		print('Tx:',tx)
		radio.send(tx)
		display.scroll(tx)
	sleep(1000)
