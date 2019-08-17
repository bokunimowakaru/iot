import radio
from microbit import *

radio.on()
print('Ready Router')
display.scroll('Router')
while True:
	tx = ''
	line = uart.readline()
	if line:
		tx = str(line, 'UTF-8')
		tx = tx.strip()
		if len(tx) > 0:
			print('Tx:',tx)
			radio.send(tx)
			display.scroll(tx)
	recv = radio.receive()
	if recv != None:
		print('Rx:',recv)
		display.scroll(recv)
