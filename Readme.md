# 🏠 ESP32 Smart Home System (MicroPython)

An integrated smart home automation system powered by **ESP32** and **MicroPython**. Features dual-cloud integration with **AWS IoT Core** and **HiveMQ Cloud**, real-time **Telegram Bot** notifications, climate monitoring, and independent voice/remote-controlled automation for door entry and lighting.

---

## ✨ Key Features

* 🚪 **Automatic Entry System (Ultrasonic Sensor + Servo + Door LED):**
  * Opens the door via servo motor (`SG90`) and turns on the entrance light (`LED4`) simultaneously when an object/person is detected within 7 cm using the ultrasonic sensor (`HC-SR04`).
  * Automatically closes the door and turns off the entrance light after 3 seconds.

* 🗣️ **Independent Voice / MQTT Remote Control:**
  * **Door Control:** Dedicated MQTT/voice commands (`door_open` / `door_close`) operate the door servo independently without affecting the light.
  * **Lighting Control:** Dedicated MQTT/voice commands (`led_on` / `led_off`) control the entrance light (`LED4`) independently without triggering the door.

* 🌡️ **Environmental & Climate Monitoring:**
  * Continuous temperature and humidity reading via **DHT11** sensor.
  * Real-time display on a **16x2 LCD** screen over **I2C**.

* ☁️ **Dual Cloud Integration:**
  * **AWS IoT Core:** Secure telemetry upload via SSL/TLS certificates and remote onboard LED control.
  * **HiveMQ Cloud MQTT:** Fast command execution via voice integration and pub/sub for sensor metrics.

* ⚠️️ **Emergency Alerts & Notifications:**
  * Visual alerts via sequential flashing pattern on 3 alert LEDs (`LED1`, `LED2`, `LED3`) when temperatures exceed 25°C.
  * Automated high-temperature warnings sent directly via **Telegram Bot**.

---

## 🛠️ Hardware Pinout

| Component | ESP32 GPIO Pin | Description / Function |
| :--- | :--- | :--- |
| **DHT11** | `GPIO 4` | Temperature & Humidity Sensor |
| **I2C LCD (SCL)** | `GPIO 22` | I2C Clock Line for LCD Display |
| **I2C LCD (SDA)** | `GPIO 21` | I2C Data Line for LCD Display |
| **HC-SR04 Trig** | `GPIO 18` | Ultrasonic Trigger Pin |
| **HC-SR04 Echo** | `GPIO 19` | Ultrasonic Echo Pin |
| **SG90 Servo** | `GPIO 5` (PWM) | Door Actuator Motor |
| **Door LED (LED4)** | `GPIO 26` | Entrance / Door Lighting |
| **Alert LED 1** | `GPIO 13` | Temperature Warning LED 1 |
| **Alert LED 2** | `GPIO 12` | Temperature Warning LED 2 |
| **Alert LED 3** | `GPIO 15` | Temperature Warning LED 3 |
| **Board LED** | `GPIO 2` | Onboard ESP32 LED |

---

## ☁️ MQTT Topics

### HiveMQ Cloud
* **`home/commands`**: Subscribes to voice and remote commands (`door_open`, `door_close`, `led_on`, `led_off`).
* **`home/esp32/led`**: Direct control of onboard LED (`ON` / `OFF`).
* **`home/esp32/dht11/Temp`**: Publishes current temperature value.
* **`home/esp32/dht11/Hum`**: Publishes current humidity value.

### AWS IoT Core
* **`sensor`**: Publishes environment telemetry in JSON format (`temprature`, `humidity`).
* **`led/control`**: Subscribes to JSON state for controlling the onboard LED.

---

## 📁 Repository Structure

`
Smart Home Project/
├── AWS.py                    # AWS IoT Core MQTT connection and SSL setup
├── dht11.py                  # Low-level DHT11 sensor driver
├── DHT11_LCD.py              # Sensor-to-LCD formatting and display integration
├── lcd_display.py            # I2C driver for 16x2 LCD screen
├── main.py                   # System entry point and primary event loop
├── mqtt_node.py              # HiveMQ Cloud MQTT connection and handler
├── Readme.md                 # Project documentation
├── servo_motor.py            # Servo motor PWM control driver
├── Tel_bot.py                # Telegram Bot notification handler
├── ultrasonic_sys.py         # Ultrasonic distance measurement module
├── voice_assistant_ESP32.py  # ESP32-side voice command parsing and actuation
├── voice_assistant_PC.py     # PC-side speech-to-text and MQTT command publisher
└── WiFi.py
## 🚀 Setup & Execution

1. **AWS Certificates:** Upload your AWS IoT certificates (`root.pem`, `device.crt`, `private.key`) directly to the ESP32 root filesystem.
2. **Upload Drivers:** Upload `esp32_i2c_lcd.py` and `lcd_api.py` to the flash memory.
3. **Configure Credentials:** Open `main.py` and update your Wi-Fi credentials (`SSID`, `PASS`), HiveMQ/AWS endpoints, and Telegram Bot details (`BOT_TOKEN`, `CHAT_ID`).
4. **Run System:** Run `main.py`. The ESP32 will connect to Wi-Fi, sync time via NTP, connect to both MQTT brokers, and begin monitoring and responding to commands.
