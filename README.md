
# Programación de un mapa meteorológico LED con MicroPython en un ESP32C3

# Resumen
En esta publicación, demostraremos cómo programar un bonito mapa del tiempo con LED utilizando un microcontrolador [ESP32C3](https://www.espressif.com/en/products/socs/esp32-c3) con [MicroPython](https://micropython.org) y datos de la [API de OpenWeatherMap](https://openweathermap.org/api).

![image](https://verpent.co/images/jpg/PHOTO-2025-02-01-01-24-57.jpg)

Foto de [Jini](https://www.instagram.com/fotosmalasperomias)

<a href="http://104.131.81.97" style="align: center;"> Servidor de CTF IoT de HackConRD 2025 Badge
# Comenzando con el desarrollo de IoT y MicroPython 
En este proyecto, mostraremos información meteorológica en el mapa de la RD🇩🇴. 
Además, este proyecto servirá como el distintivo para [HackConRD 2025](https://hackconrd.org), donde organizaremos un [CTF](http://104.131.81.97/) enfocado en la ingeniería inversa de este dispositivo IoT temático.
# Hardware y Software
El ESP32C3 es un microcontrolador potente y rentable con Wi-Fi y Bluetooth integrados, lo que lo convierte en una excelente opción para proyectos de IoT.  Una aplicación clave del IoT es el monitoreo del clima en tiempo real, donde los microcontroladores recopilan datos ambientales de sensores o, en nuestro caso, de fuentes de Internet.
<p align="center"><img src="https://verpent.co/images/jpg/IMG_2654.jpg"/> <br><br>Placa de expansión ESP32C3</p>
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
```esptool.py --port /dev/tty.usbmodem1421201 borrar_flash```
Escribe el binario del firmware de MicroPython en la memoria flash del ESP32C3:
```esptool.py --chip esp32c3 --port /dev/tty.usbmodem1421201 write_flash -z 0x00 ESP32_GENERIC_C3-20241129-v1.24.1.bin```
# Escribe el código que se ejecutará en el chip del microcontrolador
En tu editor de código favorito, comienza importando las bibliotecas necesarias para ejecutar el proyecto:
<script src="https://gist.github.com/jrgdiaz/c689d9af940a58c802fc8948866508dd.js"> </script> </script>
Luego escribe una función que se conecte a un punto de acceso Wi-Fi:
<script src="https://gist.github.com/jrgdiaz/2c05c11a2a223384a23fecb44e3d195a.js"> </script> </script>
La parte principal del código es traducir los datos meteorológicos al color del LED en la placa, aquí está el código para eso:
<script src="https://gist.github.com/jrgdiaz/26fb618d90c4da3297b7138f08e80d2e.js"></script>
Y finalmente, nuestra función principal de entrada main.py.
<script src="https://gist.github.com/jrgdiaz/7d53ec2555d0776cc3274d777b63134b.js"> </script>
# Visualizando datos meteorológicos
Para representar las condiciones meteorológicas, estamos utilizando una matriz de 31 LED aRGB, con cada LED correspondiente a una de las 31 provincias.  Los LED cambiarán de color según las condiciones meteorológicas:
<p align="center"><img src="https://verpent.co/images/jpg/IMG_2638.jpg"/> Contexto: <p align="center"><img src="https://verpent.co/images/jpg/IMG_2638.jpg"/> <br><br> Diseño de PCB por <a href=""> \nTexto a traducir: <br><br> Diseño de PCB por <a href=""> Emeraldo Ramos</a></p>
- **Rojo**: Temperaturas altas
- **Amarillo**: Buen tiempo
- **Verde**: Condiciones frescas pero secas
- **Azul**: Lluvia intensa
Esto proporciona una manera intuitiva de visualizar rápidamente los patrones climáticos en todo el país.
