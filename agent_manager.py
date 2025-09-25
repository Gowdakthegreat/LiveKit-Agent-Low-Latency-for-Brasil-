# agent_manager.py
import subprocess
import os

RUNNING_AGENTS = {}

def start_agent(agent_name: str, instructions: str, voice_id: str):
    if agent_name in RUNNING_AGENTS and RUNNING_AGENTS[agent_name].poll() is None:
        return {"status": "already_running", "pid": RUNNING_AGENTS[agent_name].pid}

    print(f"Iniciando agente '{agent_name}' via linha de comando...")

    env = os.environ.copy()
    env["AGENT_INSTRUCTIONS"] = instructions
    env["AGENT_VOICE_ID"] = voice_id

    command = ["poetry", "run", "python", "src/agent.py", "start"]
    process = subprocess.Popen(command, env=env)

    RUNNING_AGENTS[agent_name] = process
    print(f"Agente '{agent_name}' iniciado com PID: {process.pid}")
    return {"status": "started", "pid": process.pid}

def stop_agent(agent_name: str):
    if agent_name not in RUNNING_AGENTS:
        return {"status": "not_found"}
    process = RUNNING_AGENTS[agent_name]
    process.terminate()
    del RUNNING_AGENTS[agent_name]
    print(f"Agente '{agent_name}' parado.")
    return {"status": "stopped"}