import machine
import time
import sys

print("Teste") # Testando actions
sys.stdout.flush()

# simplificando pinos de leitura
PIN_LED_GREEN = 2
PIN_LED_YELLOW = 4
PIN_LED_RED = 5
PIN_BUZZER = 18

TOTAL_TIME = 10  
GREEN_LIMIT = 4
YELLOW_LIMIT = 7
RED_LIMIT = 10

led_green = machine.Pin(PIN_LED_GREEN, machine.Pin.OUT)
led_yellow = machine.Pin(PIN_LED_YELLOW, machine.Pin.OUT)
led_red = machine.Pin(PIN_LED_RED, machine.Pin.OUT)

buzzer = machine.PWM(machine.Pin(PIN_BUZZER))
buzzer.duty(0)


def update_display(line1, line2=""):
    print("\n" + "="*20)
    print(f"| {line1.center(16)} |")
    print(f"| {line2.center(16)} |")
    print("="*20)

def set_leds(g, y, r):
    led_green.value(g)
    led_yellow.value(y)
    led_red.value(r)

def beep(freq=1000, duration=100):
    buzzer.freq(freq)
    buzzer.duty(512)
    time.sleep_ms(duration)
    buzzer.duty(0)

print("Teste")
print("Sistema de Estacionamento Iniciado.")
update_display("ESTACIONAMENTO", "INICIANDO")

print("Simulando entrada...")
beep(1500, 200)

start_time = time.ticks_ms()
last_blink = 0
blink_state = False

while True:
    current_time = time.ticks_ms()
    elapsed_seconds = time.ticks_diff(current_time, start_time) // 1000
    remaining = TOTAL_TIME - elapsed_seconds

    if remaining < 0:
        remaining = 0

    update_display("TEMPO RESTANTE", f"{remaining} s")

    if elapsed_seconds < GREEN_LIMIT:
        set_leds(1, 0, 0)

    elif elapsed_seconds < YELLOW_LIMIT:
        if elapsed_seconds == GREEN_LIMIT:
            beep(1200, 100)
        set_leds(0, 1, 0)

    elif elapsed_seconds < RED_LIMIT:
        if elapsed_seconds == YELLOW_LIMIT:
            beep(800, 100)
        set_leds(0, 0, 1)

    else:
        # tempo esgotado
        if time.ticks_diff(current_time, last_blink) >= 300:
            blink_state = not blink_state
            set_leds(0, 0, blink_state)

            if blink_state:
                buzzer.freq(2000)
                buzzer.duty(512)
            else:
                buzzer.duty(0)

            last_blink = current_time

        update_display("TEMPO ESGOTADO!", "PAGUE O TICKET")

    # encerra após TOTAL_TIME + 3 segundos
    if elapsed_seconds > TOTAL_TIME + 3:
        print("Encerrando simulação...")
        break

    time.sleep_ms(200)

set_leds(0, 0, 0)
buzzer.duty(0)

print("Simulação finalizada com sucesso.")

sys.exit()
