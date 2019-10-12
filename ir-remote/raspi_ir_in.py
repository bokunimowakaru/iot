#!/usr/bin/env python3
# coding: utf-8

import sys
import subprocess

ir_in_port = 4
ir_type = 'AEHA'
ir_wait_sec = 10

ir_types = ['AEHA','NEC','SIRC','AUTO']
path = './raspi_ir_in'

port_a = str(ir_in_port)
type_i = ir_types.index(ir_type)
if type_i ==3:
    type_i = 255
type_a = str(type_i)
wait_a = str(ir_wait_sec)
print(path, port_a, type_a, wait_a)

while True:
    res = subprocess.run([path, port_a, type_a, wait_a], stdout=subprocess.PIPE)
    data = res.stdout.decode().strip()
    if len(data) < 3:
        continue
    print(data)
