import time
import network
from machine import Pin, PWM
from neopixel import NeoPixel
from umqtt.simple import MQTTClient

# === Configuración WiFi y MQTT ===
ssid = 'javierolo88'
password = 'javi8887'
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)
print("Conectando a WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print('Conectado a WiFi:', wifi.ifconfig()[0])

broker = 'broker.hivemq.com'
topic = b'movimiento/control'
client = MQTTClient("esp32_sub", broker)

# === Configuración de Neopixel y Servo ===
led_pin = Pin(15, Pin.OUT)
np = NeoPixel(led_pin, 16)
servo = PWM(Pin(13), freq=50)

def mover_servo(direccion, activo):
    if not activo:
        servo.duty(0)  # Detener el servo
        return
    if direccion == 1:
        servo.duty(40)  # Posición para horario
    else:
        servo.duty(115)  # Posición para antihorario

# Función para encender todos los LEDs en color azul
def encender_leds():
    for i in range(np.n):
        np[i] = (0, 0, 255)  # Color azul
    np.write()

# Función para encender todos los LEDs en color rojo
def encender_leds_rojos():
    for i in range(np.n):
        np[i] = (255, 0, 0)  # Rojo
    np.write()

# === Callback MQTT ===
def callback(topic, msg):
    print("Mensaje recibido:", msg)
    try:
        datos = msg.decode().split(",")
        direccion = int(datos[0])
        activo = bool(int(datos[1]))

        print("Dirección:", direccion, "Activo:", activo)

        mover_servo(direccion, activo)

        # Apagar o encender LEDs según el estado
        if not activo:
            for i in range(np.n):
                np[i] = (0, 0, 0)  # Apagar los LEDs
        elif direccion == 1:
            for i in range(np.n):
                np[i] = (0, 0, 255)  # Azul
        else:
            encender_leds_rojos()  # Rojo en todos los LEDs

        np.write()

    except Exception as e:
        print("Error al procesar mensaje:", e)

# === Suscripción MQTT ===
client.set_callback(callback)
client.connect()
client.subscribe(topic)
print("Suscrito al topic:", topic)

# Encender todos los LEDs al inicio en azul
encender_leds()

# === Bucle principal ===
while True:
    client.check_msg()
    time.sleep(0.1)


