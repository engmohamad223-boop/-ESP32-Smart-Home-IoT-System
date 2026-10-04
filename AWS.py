import dht
import json
import network
import ntptime
import time
from machine import Pin
from umqtt.simple import MQTTClient

SSID: str = ""
PASS: str = ""
THING_NAME: str = ""
TOPIC_Pub: str = ""
TOPIC_Sub: str = ""
DHT_Topic: str = ""
LED_Topic: str = ""

END_POINT: str = ""

ROOT_CA = ""
CERTIFICATA = ""
PRIVATE_KEY = ""

SSL_CONFIG = {
    'key': open(PRIVATE_KEY, 'rb').read(),
    'cert': open(CERTIFICATA, 'rb').read(),
    'server_side': False,
}

DHT_PIN = 4
led = Pin(2, Pin.OUT)


def set_time():
  try:
    print("Setting time via NTP...")
    ntptime.settime()
    print("Time set successfully:", time.localtime())
  except Exception as e:
    print("Failed to set time via NTP:", e)


def WiFi_Connect() -> bool:
  sta = network.WLAN(network.STA_IF)
  sta.active(True)

  if sta.isconnected():
    return True

  print(f"Connecting to WiFi {SSID}...")
  sta.connect(SSID, PASS)

  timeout = 10
  while not sta.isconnected() and timeout > 0:
    print(".", end="")
    time.sleep(1)
    timeout -= 1

  if sta.isconnected():
    print("\nWiFi Connected! IP:", sta.ifconfig()[0])
    set_time()
    return True

  print("\nWiFi Connection Failed")
  return False


def WiFi_Reconnect():

  sta = network.WLAN(network.STA_IF)
  while not sta.isconnected():
    print("Attempting WiFi Reconnection...")
    sta.active(False)
    time.sleep(1)
    sta.active(True)
    if WiFi_Connect():
      break
    time.sleep(5)


def message_callback(topic, message):
  print(f"Received message on topic {topic} --> {message.decode()}")
  try:
    data = json.loads(message)
  except ValueError:
    print("Invalid JSON payload")
    return

  led_state = data.get("led")
  if led_state is None:
    return

  if isinstance(led_state, str):
    led_state = led_state.strip().lower()

  if led_state in ("on", True, 1, "1"):
    led.value(1)
    print("LED turned ON")
  elif led_state in ("off", False, 0, "0"):
    led.value(0)
    print("LED turned OFF")
  else:
      print("INVALID VALUE")


def connect_iot_core():
  
  while True:

    sta = network.WLAN(network.STA_IF)
    if not sta.isconnected():
      WiFi_Reconnect()

    try:
      client = MQTTClient(
          client_id=THING_NAME,
          server=END_POINT,
          port=8883,
          ssl=True,
          ssl_params=SSL_CONFIG,
      )
      print("Connecting to AWS IoT Core...")
      client.set_callback(message_callback)
      client.connect()
      print("Successfully connected to AWS IoT Core!")
      return client
    except Exception as e:
      print(f"AWS Connection failed ({e}), Retrying in 5 seconds...")
      time.sleep(5)


def subscribe(mqtt_client, topic):
  mqtt_client.subscribe(topic)
  print(f"Subscribed to topic: {topic}")


def main():
  client = connect_iot_core()
  subscribe(client, LED_Topic)

  DHT11_Sensor = dht.DHT11(Pin(DHT_PIN))
  last = time.time()

  while True:
    try:
      
      client.check_msg()

      now = time.time()
      if now - last >= 5:
        DHT11_Sensor.measure()
        temp = DHT11_Sensor.temperature()
        hum = DHT11_Sensor.humidity()

        payload = {"temprature": temp, "humidity": hum}

        client.publish(DHT_Topic, json.dumps(payload))
        print("Published:", json.dumps(payload))
        last = now

      time.sleep(0.1)

    except (OSError, Exception) as e:
      print(f"\nConnection lost ({e}). Reconnecting...")
      time.sleep(2)
      
      client = connect_iot_core()
      subscribe(client, LED_Topic)

    except KeyboardInterrupt:
      print("Program Stopped by User")
      break


main()