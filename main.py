import dht
import gc
import json
import network
import ntptime
import time
import urequests
from machine import Pin, I2C, PWM, time_pulse_us
from umqtt.simple import MQTTClient
from esp32_i2c_lcd import I2cLcd


SSID: str = "WEC2ED50"
PASS: str = "aa046646"

BOT_TOKEN = "8797987896:AAFAFyeYGS-JEcvDuI_k09kqcGE98LKGFm0"
CHAT_ID = "5405697540"

AWS_THING_NAME: str = "ESP_Thing"
AWS_ENDPOINT: str = "a3t4szt6m9csuv-ats.iot.us-east-1.amazonaws.com"
AWS_TOPIC_PUB: str = "sensor"
AWS_TOPIC_SUB: str = "led/control"

ROOT_CA = "root.pem"
CERTIFICATE = "device.crt"
PRIVATE_KEY = "private.key"

try:
    SSL_CONFIG_AWS = {
        'key': open(PRIVATE_KEY, 'rb').read(),
        'cert': open(CERTIFICATE, 'rb').read(),
        'server_side': False,
    }
except Exception as e:
    print("Warning: AWS Certificate files reading error:", e)
    SSL_CONFIG_AWS = {}

HIVEMQ_CLIENT_ID = "ESP32_SmartHome_Master"
HIVEMQ_BROKER = "135dedd9836c437b9172ab35864ccbe3.s1.eu.hivemq.cloud"
HIVEMQ_PORT = 8883
HIVEMQ_USER = "mohamedhawary"
HIVEMQ_PASS = "87654321"

HIVEMQ_TOPIC_COMMANDS = "home/commands"
HIVEMQ_TOPIC_LED = "home/esp32/led"
HIVEMQ_TOPIC_TEMP = "home/esp32/dht11/Temp"
HIVEMQ_TOPIC_HUM = "home/esp32/dht11/Hum"



i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=40000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
sensor = dht.DHT11(Pin(4))

board_led = Pin(2, Pin.OUT)      
led1 = Pin(13, Pin.OUT)           
led2 = Pin(12, Pin.OUT)           
led3 = Pin(15, Pin.OUT)         


trig = Pin(18, Pin.OUT)
echo = Pin(19, Pin.IN)
sg90 = PWM(Pin(5, mode=Pin.OUT), freq=50)
led4 = Pin(26, Pin.OUT)          


door_is_open = False
door_timer = 0
manual_led_on = False


sta = network.WLAN(network.STA_IF)

def set_ntp_time():
    try:
        print("Setting time via NTP...")
        ntptime.settime()
        print("Time set successfully:", time.localtime())
    except Exception as e:
        print("Failed to set time via NTP:", e)

def WiFi_Connect() -> bool:
    sta.active(True)
    if sta.isconnected():
        print(f"Connected Successfully to {SSID}")
        print(f"IP Address: {sta.ifconfig()[0]}")
        set_ntp_time()
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
        set_ntp_time()
        return True

    print("\nWiFi Connection Failed")
    return False

def WiFi_Reconnect() -> bool:
    while not WiFi_Connect():
        print("Reconnecting....")
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
    gc.collect()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"chat_id": CHAT_ID, "text": message})

    try:
        response = urequests.post(url, headers=headers, data=payload)
        print("Telegram HTTP Status Code:", response.status_code)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Telegram Error ({response.status_code}): {response.text}")
        response.close()
    except Exception as e:
        print("Error sending Telegram message:", e)
    finally:
        gc.collect()

def measure_distance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    duration = time_pulse_us(echo, 1, 30000)
    if duration < 0:
        return -1
    return (duration * 0.0343) / 2


def aws_message_callback(topic, message):
    print(f"AWS Received [{topic.decode()}]: {message.decode()}")
    try:
        data = json.loads(message)
        led_state = data.get("led")
        if led_state is not None:
            if isinstance(led_state, str):
                led_state = led_state.strip().lower()

            if led_state in ("on", True, 1, "1"):
                board_led.value(1)
                print("Board LED turned ON")
            elif led_state in ("off", False, 0, "0"):
                board_led.value(0)
                print("Board LED turned OFF")
            else:
                print("INVALID VALUE")
    except ValueError:
        print("Invalid JSON payload")

def hivemq_message_callback(topic, message):
    global door_is_open, door_timer, manual_led_on
    topic_str = topic.decode('utf-8')
    payload = message.decode('utf-8')
    print(f"HiveMQ Received [{topic_str}]: {payload}")

    if topic_str == HIVEMQ_TOPIC_LED:
        board_led.value(1 if payload == "ON" else 0)

    elif topic_str == HIVEMQ_TOPIC_COMMANDS:
        
        if payload in ["led_on", "LED_ON", "ON"]:
            manual_led_on = True
            led4.value(1)
            print("Voice/MQTT: Door LED Turned ON")

        elif payload in ["led_off", "LED_OFF", "OFF"]:
            manual_led_on = False
            led4.value(0)
            print("Voice/MQTT: Door LED Turned OFF")

        
        elif payload in ["door_open", "DOOR_OPEN"]:
            sg90.duty(26)            
            door_is_open = True
            door_timer = time.time()   
            print("Voice/MQTT: Door Opened")

        elif payload in ["door_close", "DOOR_CLOSE"]:
            sg90.duty(77)            
            door_is_open = False
            print("Voice/MQTT: Door Closed")

def connect_aws_iot():
    try:
        client = MQTTClient(
            client_id=AWS_THING_NAME,
            server=AWS_ENDPOINT,
            port=8883,
            ssl=True,
            ssl_params=SSL_CONFIG_AWS
        )
        client.set_callback(aws_message_callback)
        client.connect()
        client.subscribe(AWS_TOPIC_SUB)
        print("Successfully connected to AWS IoT Core!")
        return client
    except Exception as e:
        print(f"AWS Connection failed ({e})")
        return None

def connect_hivemq():
    try:
        client = MQTTClient(
            client_id=HIVEMQ_CLIENT_ID,
            server=HIVEMQ_BROKER,
            port=HIVEMQ_PORT,
            user=HIVEMQ_USER,
            password=HIVEMQ_PASS,
            keepalive=60,
            ssl=True,
            ssl_params={"server_hostname": HIVEMQ_BROKER}
        )
        client.set_callback(hivemq_message_callback)
        client.connect()
        client.subscribe(HIVEMQ_TOPIC_COMMANDS.encode())
        client.subscribe(HIVEMQ_TOPIC_LED.encode())
        print("Connected and Subscribed to HiveMQ Broker")
        return client
    except Exception as e:
        print("HiveMQ Connection Error:", e)
        return None


lcd.clear()
print_lcd("System Starting", 0, 0)

if not WiFi_Connect():
    WiFi_Reconnect()

aws_client = connect_aws_iot()
hivemq_client = connect_hivemq()

send_telegram("System Started! ESP32 is Online.")

time.sleep(1)
lcd.clear()

last_dht_time = 0
last_ultrasonic_time = 0
last_alert_time = 0

while True:
    current_time = time.time()

    
    if not sta.isconnected():
        print("WiFi Disconnected")
        WiFi_Reconnect()
        print("Connection is Back..")

    if aws_client:
        try:
            aws_client.check_msg()
        except OSError:
            print("AWS Connection Lost. Reconnecting...")
            aws_client = connect_aws_iot()

    if hivemq_client:
        try:
            hivemq_client.check_msg()
        except OSError:
            print("HiveMQ Connection Lost. Reconnecting...")
            hivemq_client = connect_hivemq()


    if time.ticks_ms() - last_ultrasonic_time > 150:
        dist = measure_distance()

    
        if 0 < dist < 7:
            sg90.duty(26)
            led4.value(1)
            door_is_open = True
            door_timer = time.time()

        
        elif door_is_open and (time.time() - door_timer >= 3):
            sg90.duty(77)
            if not manual_led_on:
                led4.value(0)
            door_is_open = False

        last_ultrasonic_time = time.ticks_ms()

    
    if current_time - last_dht_time >= 2:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()

            print_lcd(f"Temp:     {temp} C  ", 0, 0)
            print_lcd(f"Humidity: {hum} %  ", 0, 1)
            print(f"Temp: {temp}°C | Humidity: {hum}%")

            if aws_client:
                payload_aws = json.dumps({"temprature": temp, "humidity": hum})
                aws_client.publish(AWS_TOPIC_PUB, payload_aws)
                print("Published to AWS:", payload_aws)

            if hivemq_client:
                hivemq_client.publish(HIVEMQ_TOPIC_TEMP.encode(), str(temp).encode())
                hivemq_client.publish(HIVEMQ_TOPIC_HUM.encode(), str(hum).encode())

            if temp > 25 and (current_time - last_alert_time > 60):
                alert_msg = f"Warning! High Temperature Detected: {temp}°C | Humidity: {hum}%"
                send_telegram(alert_msg)
                last_alert_time = current_time

            if temp > 25:
                led1.on()
                time.sleep(0.1)
                led1.off()
                time.sleep_ms(1)

                led2.on()
                time.sleep(0.1)
                led2.off()
                time.sleep_ms(1)

                led3.on()
                time.sleep(0.1)
                led3.off()
                time.sleep_ms(1)
            else:
                led1.off()
                led2.off()
                led3.off()

        except OSError:
            print_lcd("Sensor Error!   ", 0, 0)
            print("Sensor read error")

        last_dht_time = current_time

    time.sleep_ms(10)