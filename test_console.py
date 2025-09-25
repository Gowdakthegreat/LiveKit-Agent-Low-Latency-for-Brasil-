# test_console.py
import os
import subprocess
from config import AGENTS_CONFIG

def main():
    print("--- Ferramenta de Teste de Agentes no Console ---")
    
    print("Agentes disponíveis para teste:")
    for name in AGENTS_CONFIG.keys():
        print(f"- {name}")
    
    agent_name = input("\nDigite o nome do agente que você quer testar: ")

    if agent_name not in AGENTS_CONFIG:
        print(f"Erro: Agente '{agent_name}' não encontrado no config.py.")
        return

    config = AGENTS_CONFIG[agent_name]
    instructions = config["instructions"]
    voice_id = config["voice_id"]
    model = config.get("model", "eleven_turbo_v2") # Pega o modelo ou usa um padrão

    print(f"\nIniciando o agente '{agent_name}' no modo console...")
    print("A conversa começará em breve. Para sair, aperte Ctrl + C.")

    env = os.environ.copy()
    env["AGENT_INSTRUCTIONS"] = instructions
    env["AGENT_VOICE_ID"] = voice_id
    env["AGENT_MODEL"] = model

    command = ["poetry", "run", "python", "src/agent.py", "console"]
    subprocess.run(command, env=env)

if __name__ == "__main__":
    main()