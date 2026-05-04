"""
Sistema de Estacionamento Inteligente - IoT/Wokwi

Projeto em Python para ESP32 no Wokwi. A lógica foi organizada como uma
máquina de estados não bloqueante: o loop principal lê entradas, atualiza
estado, controla atuadores e imprime evidências no monitor serial.
"""

try:
    from machine import Pin, PWM
    from time import ticks_ms, ticks_diff, sleep_ms
except ImportError:
    # Fallback simples para permitir leitura/teste de sintaxe em Python local.
    import time

    def ticks_ms():
        return int(time.monotonic() * 1000)

    def ticks_diff(a, b):
        return a - b

    def sleep_ms(ms):
        time.sleep(ms / 1000)

    class Pin:
        IN = 0
        OUT = 1
        PULL_UP = 2

        def __init__(self, pin, mode=None, pull=None):
            self.pin = pin
            self._value = 1 if mode == self.IN else 0

        def value(self, new_value=None):
            if new_value is None:
                return self._value
            self._value = int(bool(new_value))

    class PWM:
        def __init__(self, pin, freq=50):
            self.pin = pin
            self.freq_value = freq

        def freq(self, value):
            self.freq_value = value

        def duty(self, value):
            pass

        def deinit(self):
            pass


PIN_BOTAO_ENTRADA = 18
PIN_BOTAO_SAIDA = 19
PIN_LED_VERDE = 25
PIN_LED_AMARELO = 26
PIN_LED_VERMELHO = 27
PIN_BUZZER = 14
PIN_SERVO = 13

CAPACIDADE_MAXIMA = 5
TEMPO_CANCELA_ABERTA_MS = 1200
DEBOUNCE_MS = 80
INTERVALO_STATUS_MS = 3000

SERVO_FECHADO = 30
SERVO_ABERTO = 115


class BotaoComDebounce:
    """
    Detecta borda de pressionamento em botão ativo em nível baixo.
    """

    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.estado_estavel = 1
        self.ultima_leitura = 1
        self.ultima_mudanca = ticks_ms()

    def pressionado_agora(self):
        leitura = self.pin.value()
        agora = ticks_ms()

        if leitura != self.ultima_leitura:
            self.ultima_leitura = leitura
            self.ultima_mudanca = agora

        tempo_estavel = ticks_diff(agora, self.ultima_mudanca) >= DEBOUNCE_MS
        if tempo_estavel and leitura != self.estado_estavel:
            self.estado_estavel = leitura
            return self.estado_estavel == 0

        return False


class Cancela:
    """
    Controla o servo da cancela sem travar o programa.
    """

    FECHADA = "FECHADA"
    ABERTA = "ABERTA"

    def __init__(self, pin_number):
        self.servo = PWM(Pin(pin_number), freq=50)
        self.estado = self.FECHADA
        self.momento_fechamento = 0
        self.definir_angulo(SERVO_FECHADO)

    def definir_angulo(self, angulo):
        # Conversão aproximada para servo 0-180 graus em PWM de 50 Hz.
        duty = int(25 + (angulo / 180) * 100)
        self.servo.duty(duty)

    def abrir_temporariamente(self):
        self.definir_angulo(SERVO_ABERTO)
        self.estado = self.ABERTA
        self.momento_fechamento = ticks_ms() + TEMPO_CANCELA_ABERTA_MS

    def atualizar(self):
        if self.estado == self.ABERTA and ticks_diff(ticks_ms(), self.momento_fechamento) >= 0:
            self.definir_angulo(SERVO_FECHADO)
            self.estado = self.FECHADA


class AlarmeSonoro:
    """
    Emite bipes curtos sem usar delays longos.
    """

    def __init__(self, pin_number):
        self.buzzer = PWM(Pin(pin_number), freq=1500)
        self.buzzer.duty(0)
        self.desligar_em = 0

    def bip(self, duracao_ms=120):
        self.buzzer.duty(400)
        self.desligar_em = ticks_ms() + duracao_ms

    def atualizar(self):
        if self.desligar_em and ticks_diff(ticks_ms(), self.desligar_em) >= 0:
            self.buzzer.duty(0)
            self.desligar_em = 0


class EstacionamentoInteligente:
    """
    Máquina de estados principal do estacionamento.
    """

    def __init__(self):
        self.botao_entrada = BotaoComDebounce(PIN_BOTAO_ENTRADA)
        self.botao_saida = BotaoComDebounce(PIN_BOTAO_SAIDA)
        self.led_verde = Pin(PIN_LED_VERDE, Pin.OUT)
        self.led_amarelo = Pin(PIN_LED_AMARELO, Pin.OUT)
        self.led_vermelho = Pin(PIN_LED_VERMELHO, Pin.OUT)
        self.cancela = Cancela(PIN_SERVO)
        self.alarme = AlarmeSonoro(PIN_BUZZER)
        self.vagas_ocupadas = 0
        self.proximo_status = 0
        self.atualizar_sinalizacao()

    @property
    def vagas_livres(self):
        return CAPACIDADE_MAXIMA - self.vagas_ocupadas

    def registrar_entrada(self):
        if self.vagas_ocupadas < CAPACIDADE_MAXIMA:
            self.vagas_ocupadas += 1
            self.cancela.abrir_temporariamente()
            self.alarme.bip()
            self.atualizar_sinalizacao()
            print("ENTRADA autorizada | Ocupadas: {} | Livres: {}".format(
                self.vagas_ocupadas, self.vagas_livres
            ))
        else:
            self.alarme.bip(350)
            print("ENTRADA negada: ESTACIONAMENTO LOTADO")

    def registrar_saida(self):
        if self.vagas_ocupadas > 0:
            self.vagas_ocupadas -= 1
            self.cancela.abrir_temporariamente()
            self.alarme.bip()
            self.atualizar_sinalizacao()
            print("SAIDA autorizada | Ocupadas: {} | Livres: {}".format(
                self.vagas_ocupadas, self.vagas_livres
            ))
        else:
            self.alarme.bip(250)
            print("SAIDA ignorada: estacionamento ja esta vazio")

    def atualizar_sinalizacao(self):
        lotado = self.vagas_ocupadas >= CAPACIDADE_MAXIMA
        quase_lotado = self.vagas_ocupadas == CAPACIDADE_MAXIMA - 1

        self.led_verde.value(1 if not lotado and not quase_lotado else 0)
        self.led_amarelo.value(1 if quase_lotado else 0)
        self.led_vermelho.value(1 if lotado else 0)

    def imprimir_status_periodico(self):
        agora = ticks_ms()
        if ticks_diff(agora, self.proximo_status) >= 0:
            self.proximo_status = agora + INTERVALO_STATUS_MS
            print("ESTACIONAMENTO | ocupadas={} livres={} cancela={}".format(
                self.vagas_ocupadas, self.vagas_livres, self.cancela.estado
            ))

    def atualizar(self):
        if self.botao_entrada.pressionado_agora():
            self.registrar_entrada()

        if self.botao_saida.pressionado_agora():
            self.registrar_saida()

        self.cancela.atualizar()
        self.alarme.atualizar()
        self.imprimir_status_periodico()


def main():
    sistema = EstacionamentoInteligente()
    print("ESTACIONAMENTO INTELIGENTE iniciado")
    print("Pressione ENTRADA para ocupar vaga e SAIDA para liberar vaga")

    while True:
        sistema.atualizar()
        sleep_ms(50)


main()
