import radio
from microbit import *

radio.on()
print('Ready mic')
display.scroll('mic')
val = 0
while True:
	val_prev = val
	val = microphone.sound_level()
	if val - val_prev >= 5:
		tx = str(val)
		print('Tx:',tx)
		radio.send(tx)
		display.scroll(tx)
		sleep(900)
	sleep(100)
