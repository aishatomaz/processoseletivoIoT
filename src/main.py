import machine
import time

PIN_LED_GREEN = 2
PIN_LED_YELLOW = 4
PIN_LED_RED = 5
PIN_BUZZER = 18
PIN_BTN_START = 14
PIN_BTN_RESET = 27

TOTAL_TIME = 20 
GREEN_LIMIT = 10  # Até 10s fica verde
YELLOW_LIMIT = 15 # De 10s a 15s fica amarelo
RED_LIMIT = 20    # De 15s a 20s fica vermelho fixo

led_green = machine.Pin(PIN_LED_GREEN, machine.Pin.OUT)
led_yellow = machine.Pin(PIN_LED_YELLOW, machine.Pin.OUT)
led_red = machine.Pin(PIN_LED_RED, machine.Pin.OUT)
buzzer = machine.PWM(machine.Pin(PIN_BUZZER))
buzzer.duty(0)

btn_start = machine.Pin(PIN_BTN_START, machine.Pin.IN, machine.Pin.PULL_UP)
btn_reset = machine.Pin(PIN_BTN_RESET, machine.Pin.IN, machine.Pin.PULL_UP)

timer_running = False
start_time = 0
elapsed_seconds = 0

last_blink = 0
blink_state = False

def update_display(line1, line2=""):
    """Simula o display LCD via Serial"""
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

print("Sistema de Estacionamento Iniciado.")
update_display("ESTACIONAMENTO", "AGUARDANDO CARRO")

while True:
    current_time = time.ticks_ms()

    # Botão de entrada
    if not btn_start.value() and not timer_running:
        timer_running = True
        start_time = time.ticks_ms()
        beep(1500, 200)
        print("Carro detectado! Iniciando contagem de gratuidade.")

    # Botão de saída
    if not btn_reset.value():
        if timer_running:
            timer_running = False
            set_leds(0, 0, 0)
            buzzer.duty(0)
            update_display("SAIDA LIBERADA", "VOLTE SEMPRE")
            time.sleep(1)
            update_display("ESTACIONAMENTO", "AGUARDANDO CARRO")
            print("Carro saiu. Sistema resetado.")

    # Lógica do Cronômetro
    if timer_running:
        elapsed_seconds = time.ticks_diff(current_time, start_time) // 1000
        remaining = TOTAL_TIME - elapsed_seconds
        
        if remaining < 0: remaining = 0

        # Atualiza Display
        update_display("TEMPO RESTANTE", f"{remaining} segundos")

        if elapsed_seconds < GREEN_LIMIT:
            set_leds(1, 0, 0) # Verde
        
        elif elapsed_seconds < YELLOW_LIMIT:
            if elapsed_seconds == GREEN_LIMIT and elapsed_seconds > 0: beep(1200, 100)
            set_leds(0, 1, 0) # Amarelo
            
        elif elapsed_seconds < RED_LIMIT:
            if elapsed_seconds == YELLOW_LIMIT: beep(800, 100)
            set_leds(0, 0, 1) # Vermelho Fixo
            
        else:
            # TEMPO ESGOTADO: Vermelho Piscando + Alarme
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

    time.sleep_ms(50)