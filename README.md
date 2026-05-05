<p align="center">
  <img src="https://github.com/user-attachments/assets/d076ce24-634a-42b8-9e2a-ffa88816a7a9" width="45%" />
  <img src="https://github.com/user-attachments/assets/d076ce24-634a-42b8-9e2a-ffa88816a7a9" width="45%" />
</p>

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


O projeto simula um Sistema de Controle de Acesso para Estacionamento, desenvolvido em MicroPython para o microcontrolador **ESP32** e executado no simulador **Wokwi**. A idealização dele foi baseado no sistema de estacionamento do Cariri Garden Shopping de Juazeiro do Norte-CE, que possui um tempo de gratuidade e, após expirar o tempo limite, o cliente deve pagar pelas horas usadas do estacionamento.
O sistema gerencia até 5 vagas simultâneas e controla automaticamente a entrada e saída de veículos. Quando um veículo chega, o usuário pressiona o botão **ENTRADA**; ao sair, pressiona o botão **SAÍDA**. O sistema valida se há vaga disponível, abre a cancela (servo motor), emite um sinal sonoro e atualiza a sinalização luminosa (LEDs verde, amarelo e vermelho) de acordo com a ocupação atual.
 
Se o estacionamento estiver lotado, a entrada é bloqueada e um bipe mais longo é emitido como alerta.

---

## Ꮺ Arquitetura do Sistema Embarcado ²
 
O firmware foi estruturado como uma **máquina de estados não bloqueante**, evitando o uso de `sleep()` longos que travariam o loop principal.
 
### Fluxo principal (`main.py`)
 
```
main()
 └── EstacionamentoInteligente()
      └── loop: sistema.atualizar()  [a cada 50 ms]
           ├── BotaoComDebounce → detecta borda de pressionamento (ENTRADA / SAÍDA)
           ├── registrar_entrada() ou registrar_saida()
           │    ├── verifica capacidade
           │    ├── Cancela.abrir_temporariamente()  → servo abre por 1200 ms
           │    ├── AlarmeSonoro.bip()               → buzzer dispara por 120 ms
           │    └── atualizar_sinalizacao()           → LEDs refletem ocupação
           ├── Cancela.atualizar()   → fecha servo quando o tempo expira
           ├── AlarmeSonoro.atualizar() → desliga buzzer quando o tempo expira
           └── imprimir_status_periodico() → log serial a cada 3 s
```
 
### Classes e responsabilidades
 
| Classe | Responsabilidade |
|---|---|
| `BotaoComDebounce` | Detecta borda de descida (pressionamento) com debounce de 80 ms |
| `Cancela` | Controla o servo sem bloquear o loop (temporizador por `ticks_ms`) |
| `AlarmeSonoro` | Emite bipes de duração configurável sem `sleep` |
| `EstacionamentoInteligente` | Orquestra todos os componentes e mantém o contador de vagas |
 
### Estrutura de temporização
 
Toda temporização é feita com `ticks_ms()` e `ticks_diff()` do MicroPython, garantindo que o loop principal rode a cada 50 ms sem interrupções. Isso permite que múltiplos componentes (servo, buzzer, LEDs) sejam gerenciados de forma concorrente dentro do mesmo ciclo, sem que um bloqueie o outro.
 
### Transições de estado
 
As transições entre estados de ocupação são detectadas comparando `vagas_ocupadas` com a `CAPACIDADE_MAXIMA`. Bipes distintos são emitidos conforme o evento:
 
- **Bip curto (120 ms)** — entrada ou saída autorizada
- **Bip médio (250 ms)** — tentativa de saída com estacionamento vazio
- **Bip longo (350 ms)** — tentativa de entrada com estacionamento lotado
 
---

### │﹒ Imagem para melhor visualização
<img width="804" height="604" alt="led" src="https://github.com/user-attachments/assets/2757e44e-411f-4876-8c0b-9f23fb9ffdec" />

> OBS: Todos os leds serão acesos de acordo com os padrões estabelecidos e falados anterioremente. 


## Ꮺ Componentes Utilizados na Simulação ³
 
| Componente | ID Wokwi | GPIO | Função |
|---|---|---|---|
| ESP32 DevKit C v4 | `esp` | — | Microcontrolador principal |
| Pushbutton (verde) | `btnEntrada` | GPIO 18 | Registra entrada de veículo |
| Pushbutton (azul) | `btnSaida` | GPIO 19 | Registra saída de veículo |
| LED Verde | `ledVerde` | GPIO 25 | Indica vagas disponíveis |
| LED Amarelo | `ledAmarelo` | GPIO 26 | Alerta: última vaga disponível |
| LED Vermelho | `ledVermelho` | GPIO 27 | Indica estacionamento lotado |
| Resistores 220 Ω | `rVerde`, `rAmarelo`, `rVermelho` | — | Limitação de corrente nos LEDs |
| Buzzer | `buzzer` | GPIO 14 | Sinal sonoro de confirmação ou alerta |
| Servo Motor | `servoCancela` | GPIO 13 | Cancela de acesso (30° fechada / 115° aberta) |
 
### Lógica de sinalização dos LEDs
 
| Estado | LED Verde | LED Amarelo | LED Vermelho |
|---|---|---|---|
| Vagas livres (0–3 ocupadas) | ✅ Ligado | ❌ | ❌ |
| Quase lotado (4 ocupadas) | ❌ | ✅ Ligado | ❌ |
| Lotado (5 ocupadas) | ❌ | ❌ | ✅ Ligado |
 
---
 
## Ꮺ Decisões Técnicas Relevantes ⁴
 
**Loop não bloqueante:** A principal decisão de arquitetura foi evitar qualquer `sleep()` dentro do loop principal. Toda temporização usa `ticks_ms()`, permitindo que botões, servo e buzzer sejam atualizados de forma concorrente dentro do mesmo ciclo de 50 ms.
 
**Debounce por software:** A classe `BotaoComDebounce` implementa detecção de borda estável — só reconhece um pressionamento se o sinal permanecer estável por pelo menos 80 ms, eliminando leituras espúrias sem necessidade de hardware adicional.
 
**Encapsulamento em classes:** Cada componente físico foi encapsulado em uma classe com responsabilidade única, facilitando leitura, manutenção e eventual expansão do sistema (ex: adicionar mais sensores ou trocar o servo por outro atuador).
 
**Constantes nomeadas no topo do arquivo:** Todos os valores de configuração (pinos, capacidade, tempos) foram definidos como constantes, separando configuração de lógica e facilitando ajustes sem alterar o código funcional.
 
**Fallback para Python local:** O bloco `try/except ImportError` permite executar e testar a sintaxe do código em Python padrão (sem MicroPython), agilizando o desenvolvimento antes de subir para simulação.
 
**Saída serial estruturada:** Todas as mensagens de log seguem um padrão consistente (`ENTRADA autorizada`, `SAIDA autorizada`, `ESTACIONAMENTO LOTADO`), permitindo que o pipeline de CI valide o comportamento correto via `expect_text`.
 
---
 
## Ꮺ Resultados Obtidos ⁵
 
- O sistema inicializa corretamente e imprime o banner `ESTACIONAMENTO INTELIGENTE iniciado` no monitor serial
- Pressionamento do botão **ENTRADA** com vagas disponíveis → cancela abre, LED atualiza, bip curto emitido
- Pressionamento do botão **ENTRADA** com estacionamento lotado → cancela permanece fechada, bip longo de alerta
- Pressionamento do botão **SAÍDA** com veículos presentes → cancela abre, contador decrementa, sinalização atualiza
- Pressionamento do botão **SAÍDA** com estacionamento vazio → operação ignorada com bip de aviso
- Cancela fecha automaticamente após **1200 ms** sem bloquear demais operações
- Status periódico impresso no monitor serial a cada **3 segundos**
- O pipeline do **GitHub Actions** valida o texto `ESTACIONAMENTO` na saída serial, confirmando inicialização correta
**Requisitos atendidos:**
  > <img width="485" height="148" alt="pipeline" src="https://github.com/user-attachments/assets/9fe3c28f-2f27-4cc1-ba48-96d11ab7a633" />

 
- ✦ Estrutura mínima de arquivos (`src/main.py`, `diagram.json`, `wokwi.toml`, `README.md`)
- ✦ Código organizado e legível com classes e constantes
- ✦ Simulação funcional no Wokwi
- ✦ Pipeline de CI executando sem falhas
- ✦ Commits com mensagens descritivas
---
 
## Ꮺ Comentários Adicionais ⁶
 
**Aprendizados:** O maior aprendizado foi a adaptação ao modelo de programação não bloqueante exigido por sistemas embarcados com loop único. Diferente de aplicações desktop, não é possível simplesmente "pausar" a execução — todos os componentes precisam ser gerenciados de forma cooperativa dentro do mesmo ciclo de atualização. O uso do Wokwi integrado ao GitHub Actions também foi um aprendizado valioso sobre CI/CD aplicado a hardware simulado, parte essa que foi dedicado cerca de 3 dias para resolução do problema, testando vários repositórios e modos de executar a mesma ideia do projeto.
 
**Melhorias possíveis com mais tempo:**
- Substituir os botões por sensores infravermelhos ou ultrassônicos para detecção automática de veículos
- Adicionar um display LCD ou OLED para exibir o número de vagas em tempo real
- Implementar comunicação MQTT para monitoramento remoto do status do estacionamento
- Persistir o contador de vagas em memória não-volátil (NVS) para sobreviver a reinicializações
- Adicionar múltiplas cancelas com controle independente para entrada e saída simultâneas

<p align="center">
  <img src="https://github.com/user-attachments/assets/d076ce24-634a-42b8-9e2a-ffa88816a7a9" width="45%" />
  <img src="https://github.com/user-attachments/assets/d076ce24-634a-42b8-9e2a-ffa88816a7a9" width="45%" />
</p>

