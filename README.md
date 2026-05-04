# Sistema de Controle de Estacionamento com Temporizador

> Projeto desenvolvido para o processo seletivo **Intensivo Maker | IoT** – Etapa Prática de Sistemas Embarcados.
---

## —﹒Identidade do Candidato ﹒  <img width="40" height="40" alt="light board sticker _ Sparkles Effects Sticker - Find   Share on GIPHY" src="https://github.com/user-attachments/assets/eb3221b1-c5fc-4645-9125-9413ff64b102" />              


- **Nome completo:** *Ana Aisha Tomaz de Morais*
- Curso: Engenharia de Software - UFCA (3° Semestre)                                                                                                                                                                          
- **GitHub:** [*@aishatomaz*](https://github.com/aishatomaz)
- **EMAIL:** *aisha.tomaz@aluno.ufca.edu.br*

---

##  Ꮺ Visão Geral da Solução ¹ 


O projeto simula um **sistema de controle de tempo de permanência em uma vaga de estacionamento** utilizando um ESP32 com MicroPython. Ao ser acionado, o sistema inicia uma contagem regressiva de 10 segundos e sinaliza progressivamente o nível de urgência por meio de LEDs coloridos, sinais sonoros e mensagens em um display LCD. A ideia do projeto é advindo do atual sistema do Cariri Garden Shopping de Juazeiro do Norte-CE, o mesmo não possui um sistema que sinaliza o tempo de permanência, algo que fica a critério do cliente ficar em constante verificação.

O comportamento do sistema pode ser resumido assim:

| Fase              | Tempo       | LED       | Buzzer | LCD                     |
|-------------------|-------------|-----------|--------|--------------------------|
| Entrada / Normal  | 0 – 4 s     | 🟢 Verde  | Beep   | `TEMPO RESTANTE / X s`  |
| Atenção           | 4 – 7 s     | 🟡 Amarelo| Beep   | `TEMPO RESTANTE / X s`  |
| Crítico           | 7 – 10 s    | 🔴 Vermelho| Beep  | `TEMPO RESTANTE / X s`  |
| Tempo esgotado    | > 10 s      | 🔴 Piscando| Alarme| `TEMPO ESGOTADO! / PAGUE O TICKET` |

O botão **Entrada** simula a chegada de um veículo e o botão **Saída** representa a liberação da vaga (ambos conectados no circuito e disponíveis para expansão futura da lógica).

---

## Ꮺ Arquitetura do Sistema Embarcado ²

### Fluxo principal (`main.py`)

```
Inicialização dos pinos (GPIO, PWM, LCD via print serial)
              │
              ▼
        Beep de entrada
              │
              ▼
  ┌──────────────────────────────────────┐
  │          Loop principal              │  ← executa a cada 200 ms
  │                                      │
  │  1. Calcula tempo decorrido          │
  │  2. Define fase (verde/amarelo/red)  │
  │  3. Aciona LED correspondente        │
  │  4. Emite beep na transição de fase  │
  │  5. Exibe tempo restante no LCD      │
  │  6. Se esgotado: pisca LED + alarme  │
  └──────────────────────────────────────┘
              │
              ▼
    Encerra após TOTAL_TIME + 3 s
    (LEDs e buzzer desligados)
```
### │﹒ Imagem para melhor visualização
<img width="619" height="533" alt="leds" src="https://github.com/user-attachments/assets/c97af2a0-0e18-4606-9663-1ef67aa6b1ac" />

- OBS: Todos os leds serão acesos de acordo com os padrões estabelecidos e falados anterioremente. 


### Estrutura de temporização

O sistema usa `time.ticks_ms()` e `time.ticks_diff()` para medir o tempo decorrido com precisão desde o início da simulação, sem depender de `time.sleep()` no loop principal — o que permite que o loop execute a cada 200 ms e reaja rapidamente a eventos como o piscar do LED no estado de alarme (intervalo de 300 ms).

### Transições de fase

As transições entre fases são detectadas comparando `elapsed_seconds` com as constantes `GREEN_LIMIT`, `YELLOW_LIMIT` e `RED_LIMIT`. Beeps distintos são emitidos a cada transição para alertar o usuário de forma sonora:

- **1500 Hz** na entrada
- **1200 Hz** ao entrar na fase amarela
- **800 Hz** ao entrar na fase vermelha
- **2000 Hz contínuo** no alarme de tempo esgotado

---

## Ꮺ Componentes Utilizados na Simulação ³

| Componente              | ID Wokwi      | GPIO   | Função                                                     |
|------------------------|---------------|--------|------------------------------------------------------------|
| ESP32 DevKit V1        | `esp`         | —      | Microcontrolador principal                                 |
| LED Verde              | `led_green`   | D2     | Sinaliza fase inicial — vaga OK, tempo confortável         |
| LED Amarelo            | `led_yellow`  | D4     | Sinaliza fase de atenção — tempo reduzido                  |
| LED Vermelho           | `led_red`     | D5     | Sinaliza fase crítica e alarme — tempo esgotado            |
| Buzzer                 | `bz1`         | D18    | Emite beeps de transição e alarme contínuo (PWM)           |
| Botão Entrada          | `btn_start`   | D14    | Simula chegada do veículo na vaga                          |
| Botão Saída            | `btn_reset`   | D27    | Simula saída / liberação da vaga                           |
| Display LCD 16x2       | `lcd1`        | D21/D22| Exibe tempo restante e mensagens de estado (I²C)           |

---

## Ꮺ Decisões Técnicas Relevantes ⁴

**Separação em funções nomeadas:** As operações de exibição (`update_display`), controle de LEDs (`set_leds`) e emissão sonora (`beep`) foram isoladas em funções, tornando o loop principal legível e facilitando manutenção.

**Uso de `ticks_ms` em vez de `sleep` no loop:** O loop principal usa `time.sleep_ms(200)` apenas como cadência mínima, mas toda a lógica temporal é baseada em `ticks_diff`. Isso permite que o piscar do LED de alarme (300 ms) funcione corretamente dentro do mesmo loop sem bloquear a execução.

**Constantes de limiar no topo do arquivo:** `TOTAL_TIME`, `GREEN_LIMIT`, `YELLOW_LIMIT` e `RED_LIMIT` são definidas como constantes nomeadas, seguindo boas práticas — qualquer ajuste de temporização é feito em um único lugar sem tocar na lógica.

**PWM no buzzer com frequências distintas por fase:** Cada transição emite uma frequência diferente (1500 → 1200 → 800 Hz), criando uma linguagem sonora intuitiva: frequências decrescentes indicam urgência crescente.

**Saída serial como substituto do LCD:** A função `update_display` faz `print` formatado no monitor serial, compatível com o ambiente de simulação e com o `expect_text` validado pelo pipeline do GitHub Actions.

**Encerramento limpo com `sys.exit()`:** Após o fim da simulação, o código desliga todos os periféricos e encerra o processo, garantindo que o pipeline de CI finalize corretamente sem timeout.

---

## Ꮺ Resultados Obtidos ⁵

- O sistema inicializa, exibe o banner `ESTACIONAMENTO` no serial e emite um beep de entrada
- O LED verde acende nos primeiros 4 segundos, indicando tempo confortável
- Ao atingir 4 segundos, o sistema transiciona para o LED amarelo com beep de alerta
- Ao atingir 7 segundos, o LED vermelho acende com beep de aviso crítico
- Após 10 segundos, o LED vermelho começa a piscar e o buzzer emite alarme contínuo, com a mensagem `TEMPO ESGOTADO! / PAGUE O TICKET` no display
- Aos 13 segundos, todos os periféricos são desligados e a simulação encerra com a mensagem `Simulação finalizada com sucesso.`
- O pipeline do GitHub Actions não executa, não gerando o print necessário para dar continuidade ao teste.

---

## Ꮺ Comentários Adicionais ⁶

**Aprendizados:** O maior desafio foi entender como o pipeline de CI funciona em conjunto com o Wokwi CLI, principalmente com o uso do Github Actions que em diferentes repositórios não apresentava erro. No mais, a utilização do mesmo servirá de ensinamento para projetos futuros.

**Melhorias possíveis com mais tempo:**
- Implementar leitura real dos botões de Entrada e Saída via interrupção (`machine.Pin.IRQ_FALLING`) para reiniciar o temporizador dinamicamente
- Escrever diretamente no LCD via I²C usando a biblioteca `lcd_api` em vez de simular pelo serial
- Adicionar múltiplas vagas com LEDs independentes, escalando o sistema para um estacionamento real
- Salvar o histórico de uso em memória flash usando `uos` e `ujson`

**Limitação atual:** Os botões de Entrada e Saída estão presentes no circuito mas ainda não estão integrados à lógica do `main.py` — a simulação inicia automaticamente sem aguardar o acionamento do botão. Esta integração seria a próxima evolução natural do projeto.
