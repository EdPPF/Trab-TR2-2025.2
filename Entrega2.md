Considerando qie a arquitetura final será:

Nó Sensor (Arduino) --(LoRa)--> Gateway (Arduino) --(Serial USB)--> PC (Script Python) --(HTTP)--> Servidor (server.py)

Os passos para o entregável 2 são:

1. Lógica que não depende do hardware
- Criar um script py que serve para ler os dados da porta serial (que vêm do gateway), converter em JSON e enviar para o server.py;
- Definir um protocolo de comunicação serial (LoRa->Serial): `id=rack1;temp=22;umid=45.2;poeira=30.1\n`
- Testar sem o hardware. Podemos modificar o script para ler o `input()` em vez do serial. Executamos o script manualmente e verificamos se os dados chegam certo.
- Código do Arduino. Tem o cliente LoRa e o gateway LoRa.

2. Integração com Hardware.