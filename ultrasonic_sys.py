from machine import Pin ,Timer,time_pulse_us
from machine import Pin,PWM
import time

trig=Pin(18,Pin.OUT)
echo=Pin(19,Pin.IN)

sg90 = PWM(Pin(5, mode=Pin.OUT))
sg90.freq(50)

led4=Pin(26,Pin.OUT)


tim0=Timer(0)

def meaure_distance(t):
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    duration=time_pulse_us(echo,1,30000)
    
    if duration <0:
        print("Time out")     
        
    else:
        distance_cm=(duration * 0.0343) /2
        print("Distance: {:.2f} c,".format(distance_cm))
        
        if distance_cm < 7:
            sg90.duty(26)
            led4.value(1)
            
        
            
            
        else:
            led4.value(0)
            sg90.duty(77)
            
            
        
 
        
tim0.init(period=500, mode=Timer.PERIODIC, callback=meaure_distance)

while True:
    pass