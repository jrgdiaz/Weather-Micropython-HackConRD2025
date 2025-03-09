---
title: Programación de un mapa meteorológico LED con MicroPython en un ESP32C3
date: Feb 28, 2025
author: Jorge Diaz
---

# Si estas en HackConRD 2025, y te gustó este proyecto (o el <a href="http://104.131.81.97" style="align: center;"> CTF</a>) considera dejarme una ⭐ en este repositorio. 

# Programación de un mapa meteorológico LED con MicroPython en un ESP32C3

# Resumen
En esta publicación, demostraremos cómo programar un bonito mapa del tiempo con LED utilizando un microcontrolador [ESP32C3](https://www.espressif.com/en/products/socs/esp32-c3) con [MicroPython](https://micropython.org) y datos de la [API de OpenWeatherMap](https://openweathermap.org/api).

![image](https://verpent.co/images/jpg/PHOTO-2025-02-01-01-24-57.jpg)

Foto de [Jini](https://www.instagram.com/fotosmalasperomias)

<a href="http://104.131.81.97" style="align: center;"> Servidor de CTF IoT de HackConRD 2025 Badge

# Comenzando con el desarrollo de IoT y MicroPython 

En este proyecto, mostraremos información meteorológica en el mapa de la RD🇩🇴. 
Además, este proyecto servirá como el badge para [HackConRD 2025](https://hackconrd.org), donde organizaremos un [CTF](http://104.131.81.97/) enfocado en la ingeniería inversa de este dispositivo IoT temático.

# Hardware y Software

El ESP32C3 es un microcontrolador potente y rentable con Wi-Fi y Bluetooth integrados, lo que lo convierte en una excelente opción para proyectos de IoT.  Una aplicación clave del IoT es el monitoreo del clima en tiempo real, donde los microcontroladores recopilan datos ambientales de sensores o, en nuestro caso, de fuentes de Internet.
<p align="center"><img src="https://verpent.co/images/jpg/IMG_2654.jpg"/> <br><br>Placa ESP32C3</p>

Para construir este proyecto, necesitarás:

- Un microcontrolador ESP32C3
- Una conexión Wi-Fi
- Firmware de MicroPython instalado en el ESP32C3
- Una clave API de OpenWeatherMap

Sin más demora, comencemos a implementar el proyecto.

# Configuración del entorno de desarrollo y el firmware de MicroPython en el ESP32C3

Primero, descarga e instala [esptool](https://github.com/espressif/esptool) con PIP:

```python3 -m pip install esptool```

Antes de ejecutar nuestro código, necesitamos instalar el binario del firmware de MicroPython en el microcontrolador.  Puedes descargarlo desde el siguiente enlace:

https://micropython.org/resources/firmware/ESP32_GENERIC_C3-20241129-v1.24.1.bin

Después de descargar el binario, puedes proceder a conectar el microcontrolador a tu computadora e identificar el puerto serie con el siguiente comando:

```ls /dev/tty*```

Proceda a borrar el flash con:

```esptool.py --port /dev/tty.usbmodem1421201 erase_flash```

Escribe el binario del firmware de MicroPython en la memoria flash del ESP32C3:

```esptool.py --chip esp32c3 --port /dev/tty.usbmodem1421201 write_flash -z 0x00 ESP32_GENERIC_C3-20241129-v1.24.1.bin```

# Escribe el código que se ejecutará en el chip del microcontrolador

## Version completa del código esta incluida en este repo como **main.py**

En tu editor de código favorito, comienza importando las bibliotecas necesarias para ejecutar el proyecto:

```
import machine, neopixel
from machine import Pin
import asyncio
import struct
import time
import network
import urequests
from micropython import const
```

Luego escribe una función que se conecte a un punto de acceso Wi-Fi:

```
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
```

La parte principal del código es traducir los datos meteorológicos al color del LED en la placa, aquí está el código para eso:

```
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
        if connect_wifi("wifi (name) ssid", "password"):
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

#handle province's special characters        
def urlencode(string):
    return string.replace(" ", "%20").replace("á", "%C3%A1").replace("é", "%C3%A9").replace("í", "%C3%AD").replace("ó", "%C3%B3").replace("ú", "%C3%BA").replace("ñ", "%C3%B1").replace(",", "%2C")
```

Y finalmente, nuestra función principal de entrada main.py.

```
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
```

# Visualizando datos meteorológicos

Para representar las condiciones meteorológicas, estamos utilizando una matriz de 31 LED aRGB, con cada LED correspondiente a una de las 31 provincias.  Los LED cambiarán de color según las condiciones meteorológicas:

<p align="center"><img src="https://verpent.co/images/jpg/IMG_2638.jpg"/><br><br> Diseño de PCB por <a href=""> Emeraldo Ramos</a></p>
  
- **Rojo**: Temperaturas altas
- **Amarillo**: Buen tiempo
- **Verde**: Condiciones frescas pero secas
- **Azul**: Lluvia intensa

Esto proporciona una manera intuitiva de visualizar rápidamente los patrones climáticos en todo el país.

You can find full code as well as English translation in the following link:

Leave a ⭐ if you like the project:

https://verpent.co/posts/esp32c3-iot-dev-getting-started
