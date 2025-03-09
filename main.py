import machine, neopixel
from machine import Pin
import aioble
import asyncio
import struct
import time
import network
import urequests
from micropython import const
import sys

def connect_wifi(ssid, password):
    connected = False
    try:
        wlan = network.WLAN(network.STA_IF)
    except Exception as e:
        print(e)
        return connected     
    wlan.active(True)
    wlan.config(txpower=8) #needed due to a hardware bug see: https://roryhay.es/blog/esp32-c3-super-mini-flaw
    try:
        wlan.connect(ssid, password)
    except Exception as e:
        if 'Wifi Internal Error' == str(e):
            print(e)
            pass
            
    while not wlan.isconnected():
        time.sleep(3) 
    print("Connected to Wi-Fi:", wlan.ifconfig())
    connected = True
    return connected

def fetch_weather_for_city(city, api_key):
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    url = f"{BASE_URL}?q={city}&appid={api_key}&units=metric"
    try:
        response = urequests.get(url)
        if response.status_code in (200, 202):
            data = response.json()
            response.close()
            return data
        else:
            print(f"Error fetching weather for {city}: {response.status_code}")
            response.close()
    except Exception as e:
        print("Weather fetch error:", e)
    return None

def parse_city_weather(data):
    if not data:
        return (20, 0)  # Default values
    temp = data["main"]["temp"]
    rain_chance = min(int(data.get("rain", {}).get("1h", 0) * 20), 100)
    return (temp, rain_chance)

def weather_to_color(temperature, precipitation_chance):
    BRIGHTNESS = 0.05
    precipitation_chance = min(precipitation_chance, 100)
    
    if precipitation_chance > 50:
        return (0, 0, int((precipitation_chance / 100) * 255 * BRIGHTNESS))
    elif temperature > 30:
        return (int(min((temperature / 50) * 255, 255) * BRIGHTNESS), 0, 0)
    elif 25 <= temperature <= 30 and precipitation_chance <= 20:
        return (int(255 * BRIGHTNESS), int(255 * BRIGHTNESS), 0)
    else:
        return (0, int(max((1 - (temperature / 30)) * 255, 0) * BRIGHTNESS), 0)    

async def update_weather(np, led_map, api_key):
    while True:
        weather_data = {}
        if connect_wifi("ssid (wifi name)", "password"):
            for province, led_index in led_map.items():
                weather_data = fetch_weather_for_city(urlencode(province), api_key)
                temp, rain = parse_city_weather(weather_data)
                print("[+] Province: "+str(province)+" Temperature: "+str(temp)+" Rain Chance: "+str(rain)+" %")
                np[led_index - 1] = weather_to_color(temp, rain)
                np.write()
            print("Weather updated!")
        else:
            print("Skipping update due to Wi-Fi failure")
        await asyncio.sleep(7200)  # Update every 2 hours
def urlencode(string):
    return string.replace(" ", "%20").replace("á", "%C3%A1").replace("é", "%C3%A9").replace("í", "%C3%AD").replace("ó", "%C3%B3").replace("ú", "%C3%BA").replace("ñ", "%C3%B1").replace(",", "%2C")


async def main():
    NUM_LEDS = 31
    LEDS_PIN = 2
    np = neopixel.NeoPixel(Pin(LEDS_PIN), NUM_LEDS)
    PROVINCE_TO_LED_MAP = {  "Santo Domingo,do": 1,
    "San Cristobal,do": 2,
    "Bani,do": 4,
    "Azua,do": 5,
    "San Jose de Ocoa,do": 3,
    "Barahona,do": 6,
    "Pedernales,do": 7,
    "Jimani": 8,
    "Neiba": 9,
    "San Juan de la Maguana,do": 10,
    "Comendador,do": 11,
    "Villa Vasquez,do": 12,
    "Dajabon,do": 13,
    "San Fernando de Monte Cristi,do": 14,
    "Mao,do": 15,
    "Puerto Plata,do": 16,
    "Santiago de los Caballeros": 17,
    "Moca,do": 18,
    "Salcedo,do": 19,
    "Nagua,do": 24,
    "Samana,do": 25,
    "Monte Plata,do": 26,
    "Hato Mayor,do": 27,
    "El Seibo,do": 29,
    "La Romana,do": 30,
    "La Altagracia,do": 31,
    "San Pedro de Macoris": 28,
    "La Vega,do": 20,
    "Bonao,do": 21,
    "Cotui,do": 22,
    "San Francisco de Macoris": 23}  # Add more
    API_KEY = "openweathermap-api-key"
    await update_weather(np, PROVINCE_TO_LED_MAP, API_KEY)

asyncio.run(main())
