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
print(time.time()-t)
tmpVal = float(tmpValStr[1:5]) * 10**(float(tmpValStr[-3:]))
if (tmpValStr[0]=="-"):
    tmpVal = tmpVal * -1
print(tmpValStr)
print(tmpVal)
sleep(2)

#Turn off pin and measure voltage
led.off()
t = time.time()
print(instr.ask("MEAS:VOLT:DC? DEF,MIN"))
print(time.time()-t)
sleep(2)


instr.close()
#print(instr.ask("MEAS:RES? 1,0.003"))
#print(usbtmc.find_device())
