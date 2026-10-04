import network
import time


SSID:str = ""
PASS:str = ""
sta = network.WLAN(network.STA_IF)
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
while True:
    if not sta.isconnected():
        print("WiFi Disconnected")
        
        while not WiFi_Reconnect():
            print("Reconnect Failed.")
            print("Retrying in 5 s")
            time.sleep(5)
            
        print("Connection is Back..")
            
if WiFi_Connect():
       
    print("WiFI connected")
        
else:
    WiFi_Reconnect()
        
WiFi_Connect()      