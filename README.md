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

> TODO