Vendor - Backend de Agentes de Voz
Este projeto é uma plataforma de backend para criar, gerenciar e orquestrar múltiplos agentes de IA de voz concorrentes. Pense nele como uma Fábrica de Assistentes de Voz: em vez de ter um único robô, temos um sistema que pode criar e gerenciar vários robôs diferentes, cada um com sua própria personalidade e tarefa.

🏛️ Arquitetura do Sistema
A plataforma é dividida em quatro componentes principais, cada um com uma responsabilidade clara, funcionando como uma equipe em um restaurante.

📂 main.py - O Recepcionista
Papel: A porta de entrada do sistema (a API).

Responsabilidade: Expõe os endpoints para o mundo exterior (ex: /agentes/iniciar/{agent_name}). Ele recebe os comandos, mas não sabe como executar a tarefa. Ele apenas delega a ordem para o especialista: o Gerente.

👔 agent_manager.py - O Gerente da Fábrica
Papel: O cérebro da operação que gerencia os "funcionários" (agentes).

Responsabilidade: Recebe as ordens do main.py. Consulta o config.py para ler o perfil do agente solicitado. Inicia e para os processos dos agentes usando subprocess, garantindo que cada um rode de forma isolada. Ele também mantém uma lista de quem está trabalhando no momento.

📋 config.py - O Arquivo de Funcionários
Papel: O nosso "banco de dados" de personalidades.

Responsabilidade: Armazena as "fichas" de cada tipo de agente. Define as instructions (personalidade), voice_id (a voz), e outras configurações específicas para cada agente que a fábrica pode construir.

🤖 src/agent.py - O Funcionário (O Template do Agente)
Papel: É o agente de voz em si, o trabalhador que executa a tarefa.

Responsabilidade: Contém a lógica de um agente genérico: sabe como se conectar ao LiveKit, como usar o STT (reconhecimento de fala), o LLM (cérebro) e o TTS (síntese de voz). Ele é um "template" que, ao ser iniciado pelo Gerente, recebe uma personalidade do config.py e se transforma no agente específico (ex: Luigi do restaurante).

🌊 Fluxo de Execução: Do Pedido ao Agente Ativo
Quando você usa a API para iniciar um agente, o seguinte fluxo acontece:

O Pedido: Você acessa http://127.0.0.1:8000/docs, encontra o endpoint POST /agentes/{agent_name}/iniciar, insere restaurante_luigi e clica em "Execute".

A Recepção (main.py): A API recebe seu pedido. Ela imediatamente chama a função start_agent do Gerente, passando a ordem: "inicie o restaurante_luigi".

A Ação do Gerente (agent_manager.py): O gerente recebe a ordem, abre o config.py, lê as instruções e a voz do Luigi.

A Execução (src/agent.py): O gerente executa um novo processo de terminal (subprocess) que roda o src/agent.py. Ele "injeta" a personalidade do Luigi nesse processo através de variáveis de ambiente.

O Resultado: O agent.py, agora "vestido" de Luigi, executa sua lógica, se conecta ao LiveKit e fica pronto para trabalhar. Você vê os logs dele aparecendo no seu terminal principal.

A Confirmação: O gerente avisa ao main.py que o processo foi iniciado, e a API te retorna uma mensagem de sucesso.

🚀 Como Rodar o Projeto
Setup Inicial

Clone o repositório.

Crie o ambiente virtual e instale as dependências com poetry install.

Configuração

Crie uma cópia do arquivo env.example e renomeie para .env.local.

Preencha todas as chaves de API necessárias (LIVEKIT_*, OPENAI_*, etc.).

Executando o Servidor

No terminal, com o ambiente virtual ativo, rode o comando:

Bash

poetry run uvicorn main:app --reload
Interagindo com a API

Abra seu navegador no endereço: http://127.0.0.1:8000/docs

Use a interface interativa para iniciar, parar e verificar o status dos seus agentes.

🗺️ Estrutura de Pastas
agent-starter-python/
|
├── .venv/
├── src/
|   ├── agent.py
|   └── __init__.py
|
├── .env.local
├── agent_manager.py
├── config.py
├── main.py
└── pyproject.toml