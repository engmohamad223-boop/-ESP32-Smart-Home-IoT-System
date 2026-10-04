from machine import Pin,PWM
import time

sg90 = PWM(Pin(5, mode=Pin.OUT))
sg90.freq(50)


while True:
    sg90.duty(26)
    time.sleep(1)
    sg90.duty(123)
    time.sleep(1)