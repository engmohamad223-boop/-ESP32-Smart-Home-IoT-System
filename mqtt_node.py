import network
import time

from umqtt.simple import MQTTClient
import dht
from machine import Pin

SSID:str=""
PASS:str=""

sta = network.WLAN(network.STA_IF)
led=Pin(2,Pin.OUT)
dht_sensor=dht.DHT11(Pin(4))


def WiFi_Connect()->bool:
    sta.active(True)

    #System connected
    if sta.isconnected():
        print(f"Connected Successfully to {SSID}")
        print(f"IP Address:", sta.ifconfig()[0])
        return True
        
        print(f"Connecting to {SSID}...")
    try:
        sta.connect(SSID,PASS)
    except OSError as e:
        print(f"WiFi Connectio Failed: {e}")
        return False
    timeout:int = 10
    
    while not sta.isconnected() and timeout > 0:
        print(".", end = " ")
        time.sleep(1)
        timeout -= 1
    if sta.isconnected():
        print("WiFi Connected")
        print(f"IP: {sta.ifconfig()[0]}")
        return True
       
    print("WiFi Connectio Failed")
    return False
        
    

def WiFi_Reconnect()->bool:
    
    while not WiFi_Connect():
        
        print("Reconnecting....")
        
        #Reser WIFI
        sta.active(False)
        time.sleep(1)
        sta.active(True)
        
        time.sleep(2)
        
        
    print("WiFi Connection established")
    return True;

def WiFi_Scan()->int:
    wlan =network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Scanning.....")
    networks = wlan.scan()
    print("Scan Done...")
    
    
    n:int = len(networks)
    
    if n == 0:
        print("No Networks Found..")
    else:
        print(f"Networks Found: {n}")
        
        for i in range(n):
            ssid, bssid, channel, rssi, authmode, hidden = networks[i]
            ssid_str = ssid.decode('utf-8') if isinstance(ssid, bytes) else ssid
            
            line = "{}: {}:: {}".format(i+1, ssid_str, rssi)
            
            if authmode == 0:
                line += "- No Password Required for this network"
            else:
                line += "- Password Required for this network"
            print(line)
            time.sleep_ms(10)
    
    return n

#Initial Connection
def build_client(client_id,server,port,user=None,password=None,keepalive=60,ssl=True):
      
    client=MQTTClient(
            client_id=client_id,
            server=server,
            port=port,
            user=user,
            password=password,
            keepalive=keepalive,
            ssl=ssl,
            ssl_params={"server_hostname": server} if ssl else {}
        )
        
    return client

def mqtt_connect(client,retries=5,delay=5):
    for attempt in range(1,retries):
        try:
            client.connect()
            print("MQTT Connected to Broker")
            return True
        except OSError as e:
            print(f"MQTT connect attempt {attempt} failed:{e}")
            time.sleep(delay)
    raise Exception("Couldn't connect to MQTT Broker after retries")      

def publish(client,topic,msg,qos=0,retain=False):
    if isinstance(topic,str):
        topic=topic.encode()
    if isinstance(msg,str):
        msg=msg.encode()
    client.publish(topic, msg, retain=retain,qos=0)
    print(f"Published to {topic}:{msg}")

def subscribe(client,topic,qos=0):
    if isinstance(topic,str):
        topic=topic.encode()
    client.subscribe(topic,qos)
    print(f"subscribe to {topic}")




def mqtt_callback(topic,msg):
    print(f"MQTT msg received on {topic.decode()}:  MSG={msg}")
    
    if topic==TOPIC_LED.encode():
         led.value(1 if msg==b"ON" else 0)
    print("LED: ","ON" if msg==b"ON" else "OFF")
    
def publish_temp(client, topic):
    try:
        dht_sensor.measure()
        Temp = dht_sensor.temperature()
        publish(client, topic, str(Temp))
    except OSError as e:
        print("failed to send data")

def publish_hum(client, topic):
    try:
        time.sleep(2)
        dht_sensor.measure()
        Hum = dht_sensor.humidity()
        publish(client, topic, str(Hum))
    except OSError as e:
        print("failed to send data")
        
def super_loop(client,interval=0.3):
    try:
        while True:
            client.check_msg()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("stopped by user")
    finally:
        client.disconnect()
        print("MQTT client disconnected")
            
    

CLIENT_ID=""
BROKER=""
TOPIC_LED=""
TOPIC_TEMP=""
TOPIC_HUM=""
if WiFi_Connect():
       
    print("WiFI connected")
    client=build_client(CLIENT_ID,BROKER,port=8883,user="",password="")
    client.set_callback(mqtt_callback)
    mqtt_connect(client)
    subscribe(client,TOPIC_LED)
    publish_temp(client, TOPIC_TEMP)
    publish_hum(client, TOPIC_HUM)
    
    super_loop(client)
    
  
 
else:
    WiFi_Reconnect()
        
WiFi_Connect()  