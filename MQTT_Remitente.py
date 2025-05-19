from machine import Pin, ADC, I2C
from neopixel import NeoPixel
from umqtt.simple import MQTTClient
import network
import time
from ssd1306 import SSD1306_I2C

# === WiFi ===
ssid = 'Wokwi-GUEST'
password = ''
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)
print("Conectando a WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print('Conectado a WiFi:', wifi.ifconfig()[0])

# === MQTT ===
broker = 'broker.hivemq.com'
client = MQTTClient("esp32_pub", broker)
client.connect()
topic = b'movimiento/control'

# === Pantalla OLED ===
i2c = I2C(0, scl=Pin(2), sda=Pin(5))
oled = SSD1306_I2C(128, 32, i2c)

# === Joystick ===
joy_x = ADC(Pin(34))
joy_y = ADC(Pin(35))
joy_button = Pin(25, Pin.IN)
joy_x.atten(ADC.ATTN_11DB)
joy_y.atten(ADC.ATTN_11DB)
joy_x.width(10)
joy_y.width(10)

direccion = 1  # 1 horario, -1 antihorario
movimiento_activo = True
boton_anterior = 1
direccion_anterior = direccion  # Para comprobar si la dirección cambia

# === Bucle principal ===
while True:
    joy_x_val = joy_x.read()
    joy_y_val = joy_y.read()
    button_pressed = not joy_button.value()

    # Cambiar el estado de movimiento al presionar el botón
    if button_pressed and boton_anterior == 1:
        movimiento_activo = not movimiento_activo
    boton_anterior = joy_button.value()

    # Actualizar la dirección según el valor del joystick en X
    if joy_x_val > 600:
        direccion = 1  # Horario
        color = 'azul'
    elif joy_x_val < 400:
        direccion = -1  # Antihorario
        color = 'rojo'
    else:
        color = 'negro'

    # Solo actualizar si la dirección cambia
    if direccion != direccion_anterior:
        print("Nueva dirección:", direccion)
        direccion_anterior = direccion

        # Mostrar en pantalla OLED
        oled.fill(0)
        oled.text("Color: " + color, 0, 0)
        oled.text("Estado:", 0, 16)
        if movimiento_activo:
            oled.text("Horario" if direccion == 1 else "Antihorario", 60, 16)
        else:
            oled.text("Detenido", 60, 16)
        oled.show()

        # Enviar por MQTT solo cuando la dirección cambia
        payload = f"{direccion},{int(movimiento_activo)}"
        client.publish(topic, payload)

    # Mostrar valores de joystick y estado en la pantalla OLED
    oled.fill(0)
    oled.text("X: " + str(joy_x_val), 0, 0)
    oled.text("Y: " + str(joy_y_val), 0, 10)
    oled.text("Boton: " + str(button_pressed), 0, 20)
    oled.show()

    time.sleep(0.1)
