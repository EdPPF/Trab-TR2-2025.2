Descrição Geral

Este trabalho propõe o desenvolvimento de um sistema distribuído para **monitorar condições ambientais** (ex.: temperatura, umidade, poeira) em salas de equipamentos da universidade, empregando comunicação **LoRa** entre nós sensores e um **gateway** que transmite os dados a um **servidor** para visualização e análise.

O sistema deve integrar as seguintes camadas:
- **Aplicação:** coleta e visualização dos dados.
- **Transporte e Rede:** transmissão IP entre gateway e servidor (TCP/UDP/HTTP).
- **Enlace e Física:** comunicação LoRa entre os nós sensores e o gateway.

Cada grupo (máx. 3 alunos) deverá projetar e implementar as três camadas principais:
1. **Clientes LoRa (nós sensores)** – responsáveis pela coleta e transmissão dos dados.
2. **Gateway LoRa → IP** – recebe dados via LoRa e encaminha ao servidor.
3. **Servidor e Dashboard** – armazena, exibe e analisa as informações coletadas.

---

Requisitos Gerais

- O desenvolvimento do **servidor** e do **gateway** deve ser feito **preferencialmente com bibliotecas padrão do Python**, como:

    - `socket`, `http.server`, `json`, `threading`, `time`, `sqlite3`, `queue`, `logging`.

- É permitido o uso de bibliotecas externas **apenas para visualização ou sensores físicos** (por exemplo: `matplotlib`, `requests`, `flask`, ou bibliotecas específicas do Arduino/LoRa).

- O código deve ser modular e documentado, destacando claramente as camadas de comunicação.


---

## **Entregável 1 – Arquitetura e Protótipo Lógico** 

**Objetivo:**
Definir a arquitetura completa do sistema e desenvolver um protótipo funcional do servidor e dashboard, mesmo com dados simulados (sem hardware real).

**Escopo:**
- Definição da **arquitetura geral** (módulos, fluxos de dados e camadas).
- Escolha das tecnologias e definição de formato de mensagem (ex.: JSON).
- Implementação do **servidor** e **dashboard** utilizando **apenas bibliotecas padrão do Python**, com dados simulados.
- Exemplo: um script Python gerando dados falsos de temperatura/umidade e enviando via `socket` ou `HTTP` para o servidor.
- Dashboard inicial para exibição dos dados (pode ser em terminal ou HTML simples via `http.server`).

**Produtos esperados:**
Documento (3–4 páginas) contendo:
- Diagrama da arquitetura.
- Descrição dos módulos e formato das mensagens.
- Especificação do fluxo de dados.
- Protótipo funcional com servidor e dashboard recebendo dados simulados.

**Observações Finais**

- **Uso de bibliotecas padrão do Python é fortemente recomendado** (exceto em partes dependentes de hardware).
- O servidor deve permitir fácil substituição da fonte de dados (simulada ou real).
- O sistema deve demonstrar claramente o fluxo de camadas:
- **Aplicação → Transporte → Rede → Enlace → Física.**
- O dashboard pode ser simples, mas funcional (exibição periódica dos valores recebidos).
- A apresentação final deve incluir uma demonstração prática do sistema completo.

***

## **Entregável 2 – Integração com Hardware**

**Objetivo:**
Integrar o sistema com os componentes físicos (Arduino e LoRa), garantindo comunicação ponta a ponta.

**Escopo:**
- Implementação dos clientes LoRa com Arduino.
- Sensores reais (temperatura, umidade) ou dados simulados.
- Configuração e integração do gateway LoRa (ex.: Arduino + receptor LoRa + comunicação serial ou PC).
- Envio dos dados do gateway para o servidor via Python com bibliotecas padrão (socket, json, threading).
- Ajuste do formato das mensagens e do dashboard.

**Produtos esperados:**
- Código do cliente e do gateway.
- Demonstração da comunicação real: Cliente → Gateway → Servidor → Dashboard.
- Documento curto (2–3 páginas) descrevendo: - Integração e ajustes realizados.
- Problemas e soluções.

***

# Rodando o Projeto

Instale a(s) dependência(s):

```bash
pip install -r requirements.txt
```

Execute o servidor:
```bash
cd monitoramento-lora/server
python3 server.py
```

Abra o navegador em `http://localhost:8080`

## 1. Teste via cliente simulado (`send_simulated.py`):

Em outro terminal, execute:

```bash
cd monitoramento-lora/gateway
python3 simulated_data.py
```

Atualize a dashboard.

## 2. Teste do gateway serial sem hardware:

Em outro terminal, execute:

```bash
cd monitoramento-lora/gateway
python3 gateway_serial_forwarder.py --stdin
```

Digite por exemplo:

```bash
id=rack1;temp=25;umid=40;poeira=30
```

Atualize a dashboard.

## 3. Teste com hardware

Em outro terminal, execute:

```bash
cd monitoramento-lora/gateway
# detecção automática da porta
python3 gateway_serial_forwarder.py
# ou passagem manual da porta
python3 gateway_serial_forwarder.py --serial <porta>
```

Atualize a dashboard.

### 3.1 Apenas com sensor 

Se apenas o sensor estiver energizado, o gateway ESP não é utilizado e os dados são passados diretamente pela porta USB.

`LoRa Sensor -> ESP SENSOR -> USB/Serial -> gateway_serial_forwarder.py -> servidor -> dashboard`

### 3.2 Com sensor e gateway 

`LoRa Sensor -> ESP SENSOR -> LoRa Gateway -> ESP GATEWAY -> USB/Serial -> gateway_serial_forwarder.py -> servidor -> dashboard` 

# Estrutura do projeto

```
trab
├─ docs/
├─ monitoramento-lora/
│  ├─ arduino/
│  │  ├─ gateway_lora/gateway_lora.ino
│  │  └─ sensor_lora/sensor_lora.ino
│  ├─ dashboard/
│  │  └─ index.html
│  ├─ gateway/
│  │  ├─ gateway_serial_forwarder.py
│  │  └─ simulated_data.py
│  ├─ server/
│  │  ├─ dados.db
│  │  └─ server.py
├─ README.md
└─ requirements.txt
```

`dashboard/index.html` -> recebe os dados do banco e exibe para o usuário

`server.py` -> recebe JSON, grava no banco os dados a serem exibidos na dashboard.

`simulated_data.py` -> envia dados falsos direto via HTTP (para testes sem hardware).

`gateway_serial_forwarder.py` -> roda no PC e reenvia para o servidor HTTP.

`sensor_lora.ino` -> código que envia os dados via LoRa (simulados ou sensores reais).

`gateway_lora.ino` -> código que recebe via LoRa e envia pela USB Serial.
