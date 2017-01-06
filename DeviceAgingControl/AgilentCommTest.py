#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial, time
from binascii import unhexlify
import usbtmc

from gpiozero import LED, Button
from time import sleep

#instr = usbtmc.Instrument("USB::0x2a8d::0x1301::INSTR")
instr = usbtmc.Instrument(10893, 4865)
#print(instr.ask("*IDN?"))


#Turn on pin and measure voltage
led= LED(20)
led.off()
t = time.time()
tmpValStr = instr.ask("MEAS:VOLT:DC? 10,0.003")
print('Time elapsed 1 = ' + str(time.time()-t))
if (abs(float(tmpValStr)) < 1.0):
    tmpValStr = instr.ask("MEAS:VOLT:DC? 1,0.003")
    print('Time elapsed 2 = ' + str(time.time()-t))
    
    if (abs(float(tmpValStr)) < 0.1):
	tmpValStr = instr.ask("MEAS:VOLT:DC? 0.1,0.003")
	print('Time elapsed 3 = ' + str(time.time()-t))

print('Time elapsed total = ' + str(time.time()-t))
tmpVal = float(tmpValStr)
print(tmpValStr)
print(tmpVal)
sleep(2)

#Turn off pin and measure voltage
led.off()
t = time.time()
print(instr.ask("MEAS:VOLT:DC? DEF,MIN"))
print('Time elapsed total = ' + str(time.time()-t))
sleep(2)


instr.close()
#print(instr.ask("MEAS:RES? 1,0.003"))
#print(usbtmc.find_device())
