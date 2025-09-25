# cli.py (Versão com biblioteca de vozes)
import click
import requests
import subprocess
import sys
import os
from dotenv import load_dotenv

API_BASE_URL = "http://127.0.0.1:8000"

# --- Funções de Lógica (o que cada comando realmente faz) ---

def _iniciar_servidor():
    """Inicia o servidor backend da API com Uvicorn."""
    click.echo("🚀 Iniciando o servidor FastAPI (uvicorn)...")
    click.echo("Pressione CTRL+C para parar o servidor.")
    try:
        subprocess.run(["poetry", "run", "uvicorn", "main:app", "--reload"])
    except KeyboardInterrupt:
        click.echo("\nServidor desligado.")

def _novo_agente():
    """Define um novo agente de forma interativa."""
    click.echo("\n--- Definindo um Novo Agente ---")
    nome = click.prompt("Qual o nome único do agente?")
    instructions = click.prompt("Quais são as instruções (personalidade)?")
    voice_id = click.prompt("Qual o ID da voz do ElevenLabs?")
    
    payload = {"nome": nome, "instructions": instructions, "voice_id": voice_id}
    
    click.echo("Definindo agente na API...")
    try:
        response = requests.post(f"{API_BASE_URL}/definir_agente", json=payload)
        if response.status_code == 200 or response.status_code == 201:
             click.secho(f"\n✅ Sucesso! {response.json().get('message')}", fg="green")
        else:
            click.secho(f"\n❌ Erro da API (código {response.status_code}): {response.text}", fg="red")
    except requests.exceptions.ConnectionError:
        click.secho("\n❌ Erro: Não foi possível conectar ao servidor. O servidor está rodando?", fg="red")

def _iniciar_agente(name: str):
    """Inicia uma instância de um agente já definido."""
    click.echo(f"Enviando comando para conectar com o agente '{name}'...")
    try:
        response = requests.post(f"{API_BASE_URL}/conectar/{name}")
        if response.status_code == 200:
            click.secho(f"\n✅ Sucesso! O agente foi iniciado.", fg="green")
            click.echo("Use os dados abaixo para se conectar (ex: no LiveKit Playground):")
            click.echo(response.json())
        else:
            click.secho(f"\n❌ Erro: {response.json().get('detail')}", fg="red")
    except requests.exceptions.ConnectionError:
        click.secho("\n❌ Erro: Não foi possível conectar ao servidor. O servidor está rodando?", fg="red")

def _listar_vozes():
    """Busca e exibe a biblioteca de vozes disponíveis na ElevenLabs."""
    click.echo("\n--- 📖 Buscando Biblioteca de Vozes na ElevenLabs ---")
    
    load_dotenv(".env.local")
    api_key = os.environ.get("ELEVEN_API_KEY")
    
    if not api_key:
        click.secho("❌ Erro: A chave 'ELEVEN_API_KEY' não foi encontrada no seu arquivo .env.local.", fg="red")
        return
        
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        voices = response.json().get("voices", [])
        
        click.echo("Encontramos as seguintes vozes (ordenadas por nome):")
        for voice in sorted(voices, key=lambda v: v['name']):
            click.secho(f"\nNome: {voice['name']}", fg="cyan", bold=True)
            click.echo(f"  ID da Voz: {voice['voice_id']}")
            
            labels = voice.get('labels', {})
            label_str = ", ".join(f"{k}: {v}" for k, v in labels.items() if v)
            if label_str:
                click.echo(f"  Características: {label_str}")
        click.echo("-" * 40)

    except requests.exceptions.RequestException as e:
        click.secho(f"\n❌ Erro ao conectar com a API da ElevenLabs: {e}", fg="red")

# --- A Nova Interface Principal ---

@click.command()
@click.option('--iniciar-servidor', is_flag=True, help="Inicia o servidor backend da API.")
@click.option('--novo-agente', is_flag=True, help="Define um novo agente de forma interativa.")
@click.option('--iniciar-agente', 'agent_to_start', type=str, help="Inicia uma instância de um agente pelo NOME.")
@click.option('--listar-vozes', is_flag=True, help="Busca e exibe a biblioteca de vozes da ElevenLabs.")
def cli(iniciar_servidor, novo_agente, agent_to_start, listar_vozes):
    """Painel de controle para gerenciar a plataforma Vendor."""
    if iniciar_servidor:
        _iniciar_servidor()
    elif novo_agente:
        _novo_agente()
    elif agent_to_start:
        _iniciar_agente(agent_to_start)
    elif listar_vozes:
        _listar_vozes() # <--- NOSSA NOVA LÓGICA
    else:
        click.echo(click.get_current_context().get_help())

if __name__ == "__main__":
    cli()