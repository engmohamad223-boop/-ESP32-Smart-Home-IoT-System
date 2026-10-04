import datetime
import os
import sys
import webbrowser
import paho.mqtt.client as mqtt
import pyaudiowpatch as pyaudio

sys.modules["pyaudio"] = pyaudio
import pyjokes
import pyttsx3
import speech_recognition as sr
import wikipedia


MQTT_BROKER = ""
TOPIC = ""

client = mqtt.Client()
client.username_pw_set("", "")
client.tls_set()
client.connect(MQTT_BROKER, 8883, 120)
client.loop_start() 

r = sr.Recognizer()

print(
    "System is active and listening... (Say 'exit' or type 'cmd' to stop the program)"
)

with sr.Microphone() as source:
    # Adjust for ambient noise once at startup
    r.adjust_for_ambient_noise(source, duration=1)

    while True:
        try:
            print("\nListening...")
            audio = r.listen(source)

            
            command = r.recognize_google(audio).lower()
            print("You said:", command)

            
            if any(
                stop_word in command for stop_word in ["cmd", "exit", "stop", "quit"]
            ):
                print("Stopping program... Goodbye!")
                break

            
            if "turn on light" in command :
                client.publish(TOPIC, "led_on")
                print("Sent: led_on")

            elif "turn off light" in command:
                client.publish(TOPIC, "led_off")
                print("Sent: led_off")

            elif "open door" in command:
                client.publish(TOPIC, "door_open")
                print("Sent: door_open")

            elif "close door" in command:
                client.publish(TOPIC, "door_close")
                print("Sent: door_close")

        except sr.UnknownValueError:
            print("Could not understand audio, please try again...")
        except sr.RequestError as e:
            print(f"Speech Recognition service error: {e}")
        except Exception as e:
            print("An error occurred:", e)

# Clean disconnect
client.loop_stop()
client.disconnect()