import radio
from microbit import *

radio.on()
print('Ready Tx Rx')
display.scroll('Rdy')
while True:
	tx = None
	if button_a.was_pressed():
		tx = 'A'
	if button_b.was_pressed():
		tx = 'B'
	if tx:
		print('Tx:',tx)
		radio.send(tx)
		display.show(tx)
	recv = radio.receive()
	if recv != None:
		print('Rx:',recv)
		display.scroll(recv)
