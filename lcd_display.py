from machine import Pin, I2C
from esp32_i2c_lcd import I2cLcd
import time


i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=40000)

lcd = I2cLcd(i2c, 0x27, 2, 16)


def print_lcd(text, col=0, row=0):
    lcd.move_to(col, row)
    for char in text:
        lcd.putstr(char)
        time.sleep_ms(10) 


lcd.clear()
time.sleep_ms(100)


print_lcd("Hello World", 0, 0)
print_lcd("ESP32 LCD1602", 0, 1)