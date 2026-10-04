import dht
from machine import Pin, I2C
from esp32_i2c_lcd import I2cLcd
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=40000)
lcd = I2cLcd(i2c, 0x27, 2, 16)


sensor = dht.DHT11(Pin(4))

led1=Pin(13,Pin.OUT)
led2=Pin(12,Pin.OUT)
led3=Pin(15,Pin.OUT)


def print_lcd(text, col=0, row=0):
    lcd.move_to(col, row)
    for char in text:
        lcd.putstr(char)
        time.sleep_ms(10)

lcd.clear()
print_lcd("System Starting", 0, 0)
time.sleep(2)
lcd.clear()

while True:
    
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        print_lcd(f"Temp:     {temp} C  ", 0, 0)
        print_lcd(f"Humidity: {hum} %  ", 0, 1)
        print(f"Temp: {temp}°C | Humidity: {hum}%")
        
        if temp> 25:
            led1.on()
            time.sleep(0.1)
            led1.off()
            time.sleep(0.001)
            
            led2.on()
            time.sleep(0.1)
            led2.off()
            time.sleep(0.001)
            
            led3.on()
            time.sleep(0.1)
            led3.off()
            time.sleep(0.001)
            
        else:
            led1.off()
            led2.off()
            led3.off()
        

    except OSError:
        
        print_lcd("Sensor Error!   ", 0, 0)
        print("Sensor read error")


    time.sleep(2)