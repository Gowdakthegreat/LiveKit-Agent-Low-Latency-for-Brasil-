# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# --- Modelo de Dados ---
# Usamos Pydantic para definir um "formulário" para os dados do agente.
# Isso garante que a API sempre receberá os dados corretos.
class AgentConfig(BaseModel):
    nome: str = Field(..., description="O nome único para o seu agente.")
    instructions: str = Field(..., description="As instruções de personalidade e tarefa do agente (o prompt).")
    voice_id: str = Field(..., description="O ID da voz do ElevenLabs a ser usada.")

# --- "Banco de Dados" em Memória ---
# Para começar, vamos guardar os agentes que você criar em um dicionário.
# Ele será resetado toda vez que o servidor reiniciar.
agentes_db = {}


# --- Configuração da API ---
app = FastAPI(
    title="Vendor - Backend",
    description="API para criar e gerenciar agentes de voz dinamicamente.",
    version="0.2.0",
)


# --- Endpoints da API ---

@app.post("/agentes", status_code=201)
def criar_agente(config: AgentConfig):
    """
    Cria a definição de um novo agente e a salva em nosso "banco de dados".
    """
    if config.nome in agentes_db:
        raise HTTPException(status_code=400, detail="Um agente com este nome já existe.")
    
    agentes_db[config.nome] = config
    return {"message": f"Agente '{config.nome}' criado com sucesso!", "config": config}

@app.get("/agentes")
def listar_agentes():
    """
    Lista os nomes de todos os agentes que foram criados.
    """
    return {"agentes_criados": list(agentes_db.keys())}

@app.get("/agentes/{nome_do_agente}")
def obter_agente(nome_do_agente: str):
    """
    Retorna a configuração detalhada de um agente específico.
    """
    if nome_do_agente not in agentes_db:
        raise HTTPException(status_code=404, detail="Agente não encontrado.")
    return agentes_db[nome_do_agente]

# Futuramente, ativaremos estes endpoints:
# @app.post("/agentes/{nome_do_agente}/iniciar")
# def iniciar_agente(nome_do_agente: str): ...

# @app.post("/agentes/{nome_do_agente}/parar")
# def parar_agente(nome_do_agente: str): ...