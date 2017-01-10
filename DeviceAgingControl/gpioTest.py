from gpiozero import LED, Button
from time import sleep

led1= LED(20)
led1.off()
sleep(5)
led1.on()
sleep(1)
