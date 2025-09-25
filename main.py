# main.py (Versão com criação de agente via JSON)
import uuid
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel # Importamos a ferramenta para criar "formulários"
from livekit.api import AccessToken, VideoGrants

load_dotenv(".env.local")

# --- Modelo de Dados (Nosso "Formulário" Padrão) ---
class AgentDefinition(BaseModel):
    nome: str
    instructions: str
    voice_id: str

# Nosso "banco de dados" em memória para as definições de agentes
AGENT_DEFINITIONS = {} 

import agent_manager

app = FastAPI(
    title="VAPI Brasileira - Plataforma Dinâmica",
    version="1.1.0",
)

# --- Endpoints da API (Atualizados) ---

@app.post("/definir_agente")
def definir_agente(agent_def: AgentDefinition): # <--- MUDANÇA AQUI
    """
    Define a 'receita' de um novo agente, recebendo os dados em um pacote JSON.
    """
    AGENT_DEFINITIONS[agent_def.nome] = agent_def.dict() # Armazenamos o dicionário
    return {"message": f"Agente '{agent_def.nome}' definido com sucesso.", "definicao": agent_def}

@app.get("/definicoes")
def listar_definicoes():
    return AGENT_DEFINITIONS

@app.post("/conectar/{agent_name}")
def conectar_com_agente(agent_name: str, user_identity: str = "usuario_humano"):
    if agent_name not in AGENT_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Agente não definido. Use o endpoint /definir_agente primeiro.")

    config = AGENT_DEFINITIONS[agent_name]
    livekit_api_key = os.environ.get("LIVEKIT_API_KEY")
    livekit_api_secret = os.environ.get("LIVEKIT_API_SECRET")
    livekit_url = os.environ.get("LIVEKIT_URL")
    room_name = f"conversa-{agent_name}-{uuid.uuid4()}"

    agent_token = AccessToken(livekit_api_key, livekit_api_secret) \
        .with_identity(f"agent-{agent_name}") \
        .with_grants(VideoGrants(room_join=True, room=room_name))

    agent_manager.start_agent(agent_name, config["instructions"], config["voice_id"])

    user_token = AccessToken(livekit_api_key, livekit_api_secret) \
        .with_identity(user_identity) \
        .with_grants(VideoGrants(room_join=True, room=room_name))

    return {
        "message": "Sala criada e agente iniciado. Use estes dados para se conectar.",
        "livekit_url": livekit_url,
        "room_name": room_name,
        "user_token": user_token.to_jwt()
    }