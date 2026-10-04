import network
import time

from umqtt.simple import MQTTClient
from machine import Pin,PWM

SSID:str=""
PASS:str=""

sta = network.WLAN(network.STA_IF)
sg90 = PWM(Pin(5, mode=Pin.OUT))
sg90.freq(50)

led4=Pin(26,Pin.OUT)


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
def build_client(client_id,server,port,user=None,password=None,keepalive=60,ssl=True,ssl_params={}):
      
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




def mqtt_callback(topic, command):
    print(f"MQTT msg received on {topic.decode()}: Command={command}")
    
    if topic == TOPIC.encode():
        
        cmd = command.decode('utf-8')
        
        if cmd == "ON" or cmd == "led_on":
            led4.value(1)
            print("LED: ON")
        elif cmd == "OFF" or cmd == "led_off":
            led4.value(0)
            print("LED: OFF")
        elif cmd == "door_open":
            sg90.duty(26)  
            print("Door: Opened")
        elif cmd == "door_close":
            sg90.duty(77)  
            print("Door: Closed")
  
    
   
    
   
        
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
TOPIC=""
if WiFi_Connect():
       
    print("WiFI connected")
    client=build_client(CLIENT_ID,BROKER,port=8883,user="",password="")
    client.set_callback(mqtt_callback)
    mqtt_connect(client)
    subscribe(client,TOPIC)
    
    
    super_loop(client)
    
  
 
else:
    WiFi_Reconnect()
        
WiFi_Connect() 