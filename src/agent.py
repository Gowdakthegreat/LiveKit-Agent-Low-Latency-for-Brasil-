# src/agent.py (Versão Final e Corrigida)
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

from livekit.agents import Agent, AgentSession, JobContext, cli, WorkerOptions
from livekit.plugins import elevenlabs, deepgram, openai, silero

class Assistant(Agent):
    def __init__(self, instructions: str):
        # Esta é a versão corrigida que passa as 'instructions' para a classe mãe
        super().__init__(instructions=instructions)

async def agent_entrypoint(ctx: JobContext):
    # Lê a personalidade do ambiente, que pode ser definida pelo test_console.py ou pelo agent_manager.py
    instructions = os.environ.get("AGENT_INSTRUCTIONS", "Você é um assistente padrão.")
    voice_id = os.environ.get("AGENT_VOICE_ID", "mPDAoQyGzxBSkE0OAOKw")
    model = os.environ.get("AGENT_MODEL", "eleven_flash_v2_5")

    session = AgentSession(
        llm=openai.LLM(model="gpt-4o-mini"),
        stt=deepgram.STT(model="nova-2", language="pt-BR"),
        tts=elevenlabs.TTS(voice_id=voice_id, model=model),
        vad=silero.VAD.load(),
    )
    
    assistant = Assistant(instructions=instructions)
    await session.start(assistant)
    logging.info("Agente pronto. Comece a digitar ou falar.")

# Este bloco torna o script executável e entende comandos como 'console' ou 'start'
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=agent_entrypoint))