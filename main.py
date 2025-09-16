import machine
from machine import Pin, PWM, ADC
import time
import network
import urequests
import ntptime
import utime

"""
Autor: Diego Villota
Fecha: 13/09/25
Ciudad: Guayaquil
"""

# CONFIGURACION DE WI-FI 
SSID = "nombre de red a usar"
PASSWORD = "contraseña de red a usar"

t = utime.localtime()
hora = "{:02d}:{:02d}".format(t[3], t[4])

# Variable para ejecutar solo una vez el envio de mensaje durante un intervalo
ultimo_envio = 0
INTERVALO = 15

# VARIABLES DE ENTORNO PARA USAR LA API BOT DE TELEGRAM 
TOKEN = "(el token que te da bot father)"
CHAT_ID = "(el id del chat que te da telegram y la API de bot father en telegram)"

# Pin del sensor de gas (ADC) y buzzer (PWM)
PIN_SENSOR_DE_GAS = 34
PIN_BUZZER = 23

# Configuración (sensor de gas)
sensor_de_gas = ADC(Pin(PIN_SENSOR_DE_GAS))
sensor_de_gas.atten(ADC.ATTN_11DB)       # Rango hasta 3.6V aprox.
sensor_de_gas.width(ADC.WIDTH_12BIT)     # Resolución 0–4095

# Configuración (buzzer)
buzzer = PWM(Pin(PIN_BUZZER))
buzzer.duty(0)  
# Umbral de detección 
UMBRAL = 900         

# FUNCION PARA CONECTAR WI-FI 
def conectar_a_internet(ssid, password):
    
    # Activa la conectividad wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # si no hay conexion establecida, intenta conectar a una red (la previamente establecida en aquellas variables del inicio)
    if not wlan.isconnected():
        print('Conectando a la red...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    # muestra informacion una vez conectado 
    print('Conectado a', ssid)
    print('Dirección IP:', wlan.ifconfig()[0])



# FUNCION PARA ENVIAR UN MENSAJE AL USUARIO VIA TELEGRAM
def enviar_mensaje_telegram(mensaje):
    # define link de envio e info a mandar 
    url = "https://api.telegram.org/bot{}/sendMessage".format(TOKEN)
    data = {"chat_id": CHAT_ID, "text": mensaje}
        
    try:
        # intenta mandar el mensaje 
        response = urequests.post(url, json=data)
        response.close()
        print("Mensaje enviado a Telegram")
    except Exception as e:
        # si ha pasado algo, nos menciona el error 
        print("Error al enviar mensaje:", e)
        

# LLAMADA A LA FUNCION DE CONECTAR WIFI 
conectar_a_internet(SSID,PASSWORD)                                                    

# CODIGO EN EJECUCION CONSTANTE 
while True:
    # Leer el valor del sensor de gas
    valor_sensor_gas = sensor_de_gas.read() 
    print("Valor del sensor de gas:", valor_sensor_gas)  #indica nivel de gas por consola (para testear) - linea opcional
    # Si el valor del sensor es mayor al umbral de deteccion, hay fuga potencial
    if valor_sensor_gas > UMBRAL:
        print("¡Se detectó gas!")
        buzzer.freq(440)      # Sonido (frecuencia)
        buzzer.duty(256)      # volumen  
        time.sleep(0.5)       # pequeño delay
        buzzer.duty(0)        # silencio momentaneo
        ahora = time.time()
        if ahora - ultimo_envio >= INTERVALO:
            enviar_mensaje_telegram("Se detecto gas! , a la hora: {}".format(hora))
            ultimo_envio = ahora
    else:
        buzzer.duty(0)        # Mantiene buzzer apagado si no hay fuga potencial de gas

    # tiempo de espera a la proxima ejecucion del bucle 
    time.sleep(1)
