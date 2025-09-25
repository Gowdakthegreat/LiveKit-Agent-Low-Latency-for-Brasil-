# main.py (Versão com salvamento permanente no config.py)
import uuid
import os
import pprint
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from livekit.api import AccessToken, VideoGrants

# Carrega as variáveis de ambiente do arquivo .env.local
load_dotenv(".env.local")

# --- Modelo de Dados (Nosso "Formulário" Padrão para criar agentes) ---
class AgentDefinition(BaseModel):
    nome: str = Field(..., description="O nome único para o seu agente.")
    instructions: str = Field(..., description="As instruções de personalidade e tarefa do agente (o prompt).")
    voice_id: str = Field(..., description="O ID da voz do ElevenLabs a ser usada.")
    model: str = Field("eleven_flash_v2_5", description="O modelo de voz do ElevenLabs a ser usado.")

# --- Importação do Gerenciador de Agentes ---
import agent_manager

# --- Configuração da API ---
app = FastAPI(
    title="Vendor - Backend",
    version="1.2.0",
)

# --- Endpoints da API ---

@app.get("/")
def root():
    """Endpoint inicial para verificar se o servidor está no ar."""
    return {"status": "Backend da VAPI Brasileira está no ar!"}

@app.post("/definir_agente")
def definir_agente(agent_def: AgentDefinition):
    """
    Define a 'receita' de um novo agente e a salva permanentemente no config.py.
    """
    from config import AGENTS_CONFIG # Importa o dicionário atual do arquivo

    # Adiciona ou atualiza a definição do agente no dicionário
    AGENTS_CONFIG[agent_def.nome] = agent_def.dict()

    # Reescreve o arquivo config.py com a lista de agentes atualizada
    try:
        with open("config.py", "w", encoding="utf-8") as f:
            f.write("# config.py - Este arquivo é gerenciado automaticamente pela API.\n")
            f.write("AGENTS_CONFIG = " + pprint.pformat(AGENTS_CONFIG, indent=4, width=120))
        
        return {"message": f"Agente '{agent_def.nome}' definido e salvo permanentemente!", "definicao": agent_def}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar o arquivo de configuração: {e}")


@app.get("/definicoes")
def listar_definicoes():
    """Lista todos os agentes que foram definidos no config.py."""
    from config import AGENTS_CONFIG
    return AGENTS_CONFIG

@app.post("/conectar/{agent_name}")
def conectar_com_agente(agent_name: str, user_identity: str = "usuario_humano"):
    """
    Cria uma sala, inicia o agente nela e retorna as credenciais para o usuário se conectar.
    """
    from config import AGENTS_CONFIG # Importa para garantir que estamos lendo a versão mais atual
    
    if agent_name not in AGENTS_CONFIG:
        raise HTTPException(status_code=404, detail="Agente não definido. Use o endpoint /definir_agente primeiro.")

    config = AGENTS_CONFIG[agent_name]
    livekit_api_key = os.environ.get("LIVEKIT_API_KEY")
    livekit_api_secret = os.environ.get("LIVEKIT_API_SECRET")
    livekit_url = os.environ.get("LIVEKIT_URL")
    room_name = f"conversa-{agent_name}-{uuid.uuid4()}"

    agent_token = AccessToken(livekit_api_key, livekit_api_secret) \
        .with_identity(f"agent-{agent_name}") \
        .with_grants(VideoGrants(room_join=True, room=room_name))

    # O agent_manager agora é mais simples e só precisa saber a personalidade
    agent_manager.start_agent(agent_name, config["instructions"], config["voice_id"], config.get("model"))

    user_token = AccessToken(livekit_api_key, livekit_api_secret) \
        .with_identity(user_identity) \
        .with_grants(VideoGrants(room_join=True, room=room_name))

    return {
        "message": "Sala criada e agente iniciado. Use estes dados para se conectar.",
        "livekit_url": livekit_url,
        "room_name": room_name,
        "user_token": user_token.to_jwt()
    }