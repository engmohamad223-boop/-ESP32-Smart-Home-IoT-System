# 🏠 ESP32 Smart Home System (MicroPython)

An integrated smart home automation system based on the **ESP32** microcontroller using **MicroPython**. The project features dual-cloud integration via **AWS IoT Core** and **HiveMQ Cloud**, a **Telegram Bot** alert system, and independent voice/remote control for the door and supporting software.

---

## ✨ Key Features

* 🚪 **Automatic Door & Light System:**
  * Opens the door using a servo motor (`SG90`) and turns on the entrance light (`LED4`) automatically when a person approaches (closer than 7 cm) using an ultrasonic sensor (`HC-SR04`).
  * Automatically closes the door and turns off the light after 3 seconds.

* 🗣️ **Independent Voice / Remote Commands:**
  * Open/close the door completely independently via MQTT/Voice commands (`door_open` / `door_close`).
  * Turn on/off the entrance light completely independently via MQTT/Voice commands (`led_on` / `led_off`).

* 🌡️ **Environment & Climate Monitoring:**
  * Continuous temperature and humidity polling using a **DHT11** sensor.
  * Real-time data display on a **16x2 LCD** screen over the **I2C** protocol.

* ☁️ **Dual Cloud Integration:**
  * **AWS IoT Core:** Streams environment telemetry continuously and receives light control commands over SSL/TLS encryption.
  * **HiveMQ Cloud MQTT:** Handles fast voice command execution and publishes temperature/humidity readings.

* ⚠️ **Emergency Alerts & Notifications:**
  * Sequential flashing light pattern across alert LEDs (`LED1`, `LED2`, `LED3`) when ambient temperature exceeds 25°C.
  * Instant alert messages dispatched via **Telegram Bot** upon high-temperature detection.

---

## 📂 Project Files

The project consists of 13 source and organizational files[cite: 1]:

| File Name | Function & Description |
| :--- | :--- |
| **`AWS.py`** | Manages connection to AWS IoT Core and handles SSL encryption[cite: 1] |
| **`dht11.py`** | Defines and reads data from the DHT11 temperature & humidity sensor[cite: 1] |
| **`DHT11_LCD.py`** | Formats and processes climate metrics for display on the LCD screen[cite: 1] |
| **`lcd_display.py`** | Driver library for controlling the I2C LCD display[cite: 1] |
| **`main.py`** | Entry point executing the main application loop[cite: 1] |
| **`mqtt_node.py`** | Connects to HiveMQ Cloud server and receives control commands[cite: 1] |
| **`Readme.md`** | Project documentation and instruction file[cite: 1] |
| **`servo_motor.py`** | Controls PWM signals for the SG90 servo motor[cite: 1] |
| **`Tel_bot.py`** | Connects the project to a Telegram Bot to send emergency alerts[cite: 1] |
| **`ultrasonic_sys.py`** | Measures distance and detects presence via HC-SR04 sensor[cite: 1] |
| **`voice_assistant_ESP32.py`** | Processes voice commands and executes them on the ESP32[cite: 1] |
| **`voice_assistant_PC.py`** | PC-side voice assistant application for sending commands via MQTT[cite: 1] |
| **`WiFi.py`** | Manages Wi-Fi connection and synchronizes time via NTP[cite: 1] |

---

## 🛠️ Hardware Pinout

| Component | ESP32 GPIO Pin | Function |
| :--- | :--- | :--- |
| **DHT11** | `GPIO 4` | Temperature & Humidity Sensor |
| **I2C LCD (SCL)** | `GPIO 22` | LCD Clock Line |
| **I2C LCD (SDA)** | `GPIO 21` | LCD Data Line |
| **HC-SR04 Trig** | `GPIO 18` | Ultrasonic Trigger Pin |
| **HC-SR04 Echo** | `GPIO 19` | Ultrasonic Echo Pin |
| **SG90 Servo** | `GPIO 5` (PWM) | Door Servo Motor |
| **Door LED (LED4)** | `GPIO 26` | Entrance / Door Lighting |
| **Alert LED 1** | `GPIO 13` | Temperature Alert LED 1 |
| **Alert LED 2** | `GPIO 12` | Temperature Alert LED 2 |
| **Alert LED 3** | `GPIO 15` | Temperature Alert LED 3 |
| **Board LED** | `GPIO 2` | Onboard ESP32 LED |

---

## ☁️ MQTT Topics

### HiveMQ Cloud:
* **`home/commands`**: Receives voice and control commands (`door_open`, `door_close`, `led_on`, `led_off`).
* **`home/esp32/led`**: Direct control of the onboard LED (`ON` / `OFF`).
* **`home/esp32/dht11/Temp`**: Publishes temperature readings.
* **`home/esp32/dht11/Hum`**: Publishes humidity readings.

### AWS IoT Core:
* **`sensor`**: Publishes climate/environment telemetry in JSON format.
* **`led/control`**: Receives onboard light control status.

---

## 📦 Dependencies

Ensure the following libraries are installed on your ESP32 filesystem:
* `umqtt.simple`
* `esp32_i2c_lcd.py` / `lcd_api.py`
* `urequests`
* `ntptime` (built-in)
* `dht` (built-in)

---

## 🚀 Setup & Run

1. Upload the AWS certificate files (`root.pem`, `device.crt`, `private.key`) to your ESP32 board memory.
2. Upload all the Python source files listed above along with the LCD and MQTT libraries to the ESP32 memory.
3. Open `main.py` and configure your Wi-Fi credentials (`SSID`, `PASS`) and Telegram Bot details (`BOT_TOKEN`, `CHAT_ID`).
4. Execute `main.py`. The system will connect to Wi-Fi, sync time via NTP, and automatically start monitoring sensors and handling commands.
