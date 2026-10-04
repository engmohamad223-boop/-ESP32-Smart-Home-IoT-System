import time
import dht
from machine import Pin

dht_pin = Pin(4, Pin.IN, Pin.PULL_UP)
sensor = dht.DHT11(dht_pin)

time.sleep(2.5) 

try:
    sensor.measure()
    print("Temperature:", sensor.temperature())
    print("Humidity:", sensor.humidity())
except Exception as e:
    print("DHT11 Error:", e)