import radio
from microbit import *

radio.on()
print('Ready Temp')
display.scroll('Temp')
while True:
	tx = str(temperature())
	print('Tx:',tx)
	radio.send(tx)
	display.scroll(tx)
	sleep(5000)
