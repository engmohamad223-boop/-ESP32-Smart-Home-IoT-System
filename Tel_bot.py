import network
import dht
from machine import Pin, I2C
from esp32_i2c_lcd import I2cLcd
import time
import urequests


i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=40000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

sensor = dht.DHT11(Pin(4))


led1 = Pin(13, Pin.OUT)
led2 = Pin(12, Pin.OUT)
led3 = Pin(15, Pin.OUT)


BOT_TOKEN = ""      
CHAT_ID = ""     

SSID: str = ""
PASS: str = ""

sta = network.WLAN(network.STA_IF)

def WiFi_Connect() -> bool:
    sta.active(True)

    if sta.isconnected():
        print(f"Connected Successfully to {SSID}")
        print(f"IP Address: {sta.ifconfig()[0]}")
        return True

    print(f"Connecting to {SSID}...")
    try:
        sta.connect(SSID, PASS)
    except OSError as e:
        print(f"WiFi Connection Failed: {e}")
        return False

    timeout: int = 10
    while not sta.isconnected() and timeout > 0:
        print(".", end=" ")
        time.sleep(1)
        timeout -= 1

    if sta.isconnected():
        print("\nWiFi Connected")
        print(f"IP: {sta.ifconfig()[0]}")
        return True

    print("\nWiFi Connection Failed")
    return False


def WiFi_Reconnect() -> bool:
    while not WiFi_Connect():
        print("Reconnecting....")
        # Reset WiFi
        sta.active(False)
        time.sleep(1)
        sta.active(True)
        time.sleep(2)

    print("WiFi Connection established")
    return True


def print_lcd(text, col=0, row=0):
    lcd.move_to(col, row)
    for char in text:
        lcd.putstr(char)
        time.sleep_ms(10)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = urequests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Telegram Error ({response.status_code}): {response.text}")
        response.close()
    except Exception as e:
        print("Error sending Telegram message:", e)

lcd.clear()
print_lcd("System Starting", 0, 0)
time.sleep(2)
lcd.clear()

if not WiFi_Connect():
    WiFi_Reconnect()


send_telegram("System Started! ESP32 is Online.")
last_alert_time = 0



while True:

    if not sta.isconnected():
        print("WiFi Disconnected")
        WiFi_Reconnect()
        print("Connection is Back..")

    try:
    
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        
        print_lcd(f"Temp:     {temp} C  ", 0, 0)
        print_lcd(f"Humidity: {hum} %  ", 0, 1)
        print(f"Temp: {temp}°C | Humidity: {hum}%")

        
        if temp > 25 and (time.time() - last_alert_time > 60):
            alert_msg = f"Warning! High Temperature Detected: {temp}°C | Humidity: {hum}%"
            send_telegram(alert_msg)
            last_alert_time = time.time()

    
        if temp > 25:
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

    time.sleep(1)