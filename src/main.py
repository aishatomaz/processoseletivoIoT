import sys
import machine
import time

print("ESTACIONAMENTO")
sys.stdout.flush()

PIN_LED_GREEN = 2
PIN_LED_YELLOW = 4
PIN_LED_RED = 5
PIN_BUZZER = 18

TOTAL_TIME = 6
GREEN_LIMIT = 2
YELLOW_LIMIT = 4
RED_LIMIT = 6

led_green = machine.Pin(PIN_LED_GREEN, machine.Pin.OUT)
led_yellow = machine.Pin(PIN_LED_YELLOW, machine.Pin.OUT)
led_red = machine.Pin(PIN_LED_RED, machine.Pin.OUT)

buzzer = machine.PWM(machine.Pin(PIN_BUZZER))
buzzer.duty(0)

def set_leds(g, y, r):
    led_green.value(g)
    led_yellow.value(y)
    led_red.value(r)

def beep(freq=1000, duration=100):
    buzzer.freq(freq)
    buzzer.duty(512)
    time.sleep_ms(duration)
    buzzer.duty(0)

print("Sistema iniciado")

start_time = time.ticks_ms()

while True:

    elapsed = time.ticks_diff(time.ticks_ms(), start_time) // 1000

    if elapsed < GREEN_LIMIT:
        set_leds(1,0,0)

    elif elapsed < YELLOW_LIMIT:
        set_leds(0,1,0)

    elif elapsed < RED_LIMIT:
        set_leds(0,0,1)

    else:
        print("Simulacao finalizada")
        break

    time.sleep(0.5)

# limpa hardware
set_leds(0,0,0)
buzzer.deinit()

print("FIM")

sys.exit()