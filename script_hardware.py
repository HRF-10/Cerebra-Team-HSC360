import network
import time
import json
import dht
import urequests
from machine import Pin
from umqtt.simple import MQTTClient

# INI BUAT KONFIGURASI WIFI 
WIFI_SSID = "duapangkatdua"
WIFI_PASS = "samadenganempat"

# INI BUAT KONFIGURASI UBIDOTS (MQTT) 
MQTT_BROKER = "industrial.api.ubidots.com"
MQTT_CLIENT_ID = "esp32-wokwi"
MQTT_USER = "BBUS-kGncf3UNWbhonIiI4HK1t5m4fyygEj"
MQTT_PASSWORD = "BBUS-kGncf3UNWbhonIiI4HK1t5m4fyygEj"
DEVICE_LABEL = "esp32"
MQTT_TOPIC = "/v1.6/devices/{}".format(DEVICE_LABEL).encode()

# INI BUAT KONFIGURASI API SERVICES (MongoDB) 
API_URL = "http://192.168.137.40:5000/data"  # Ganti dengan IP server Flask

# INI BUAT INISIALISASI SENSOR & LED 
PIR_SENSOR = Pin(18, Pin.IN)
DHT_SENSOR = dht.DHT11(Pin(4))
LED_PIN = Pin(5, Pin.OUT)

# VARIABEL BUAT INDIKATOR LAMPU 
lampu = 0

# INI BUAT KONEKSI KE WIFI 
def connect_wifi():
    print("Menghubungkan ke WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASS)
    
    timeout = 10
    while not sta_if.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1

    if sta_if.isconnected():
        print("Terhubung dengan IP:", sta_if.ifconfig()[0])
    else:
        print("Gagal terhubung! Cek WiFi.")

connect_wifi()

#INI KONEKSI KE MQTT
def connect_mqtt():
    global client
    try:
        print("Menghubungkan ke MQTT...", end="")
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD, port=1883)
        client.connect()
        print("Terhubung ke Ubidots!")
    except Exception as e:
        print("Gagal koneksi ke MQTT:", str(e))
        time.sleep(5)
        connect_mqtt()

connect_mqtt()

# INI LOOP UTAMA 
while True:
    try:
        print("\nMembaca data sensor...")
        motion = PIR_SENSOR.value()
        DHT_SENSOR.measure()
        suhu = DHT_SENSOR.temperature()
        kelembaban = DHT_SENSOR.humidity()

        print(f" PIR: {motion} | Suhu: {suhu}°C | Kelembaban: {kelembaban}%")

        # Ini buat mentukan status lampu
        if suhu > 27 or motion == 1:
            LED_PIN.value(1)
            lampu = 1
        else:
            LED_PIN.value(0)
            lampu = 0

        # Data yang mau dikirim
        payload = json.dumps({
            "temperature": suhu,
            "humidity": kelembaban,
            "motion": motion,
            "lampu": lampu
        })

        # Kirim ke Ubidots (MQTT) 
        print("Mengirim data ke Ubidots:", payload)
        client.publish(MQTT_TOPIC, payload)

        # Kirim ke MongoDB lewat Flask API 
        print("Mengirim data ke MongoDB...", end=" ")
        response = urequests.post(API_URL, data=payload, headers={'Content-Type': 'application/json'})
        print("Berhasil!" if response.status_code == 200 else "Gagal!", response.text)

    except Exception as e:
        print("Error:", str(e))
        connect_wifi()
        connect_mqtt()

    time.sleep(1)