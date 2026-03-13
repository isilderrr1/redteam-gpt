from agents.redteam_agent import RedTeamAgent
import requests
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
import time

# Inizializza la console di Rich
console = Console()

def print_header():
    header_text = """
    ██████╗ ███████╗██████╗ ████████╗███████╗█████╗ ███╗   ███╗      ██████╗ ██████╗ ████████╗
    ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗████╗ ████║     ██╔════╝ ██╔══██╗╚══██╔══╝
    ██████╔╝█████╗  ██║  ██║   ██║   █████╗  ███████║██╔████╔██║ ███╗██║  ███╗██████╔╝   ██║   
    ██╔══██╗██╔══╝  ██║  ██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║ ╚══╝██║   ██║██╔═══╝    ██║   
    ██║  ██║███████╗██████╔╝   ██║   ███████╗██║  ██║██║ ╚═╝ ██║     ╚██████╔╝██║        ██║   
    ╚═╝  ╚═╝╚══════╝╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝      ╚═════╝ ╚═╝        ╚═╝   
    """
    console.print(Panel(Text(header_text, style="bold red", justify="center"), title="[bold white]Terminale Offensivo Autonomo[/bold white]"))

def check_llm_server():
    """Verifica se il server LLM locale è acceso e raggiungibile."""
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv("LOCAL_LLM_URL")
    if not url:
        return False
        
    try:
        # Tenta una connessione rapida all'endpoint dei modelli
        requests.get(f"{url}/models", timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False

def main():
    print_header()
    
    # --- MODIFICA GRACEFUL FAILURE ---
    with console.status("[bold yellow]Controllo connessione al server LLM locale...[/bold yellow]", spinner="dots"):
        if not check_llm_server():
            console.print("\n[bold red][!] ERRORE CRITICO: Server LLM non raggiungibile.[/bold red]")
            console.print("[yellow][*] Assicurati di aver avviato LM Studio o Ollama e verifica la porta nel file .env[/yellow]\n")
            return 
    
    with console.status("[bold green]Inizializzazione motore AI e caricamento strumenti in corso...", spinner="bouncingBar"):
        agent = RedTeamAgent()
        time.sleep(1)
        
    console.print("[bold green]✔️ Sistema online con Memoria Attiva.[/bold green] Digita 'esci' per terminare.\n")
    
    while True:
        try:
            user_input = console.input("[bold cyan][Comando] > [/bold cyan]")
            
            if user_input.lower() in ['exit', 'quit', 'esci']:
                console.print("\n[bold red][!] Disconnessione. Alla prossima![/bold red]")
                break
                
            if not user_input.strip():
                continue
                
            console.print("\n[bold yellow][*] Elaborazione in corso (fase di ricognizione e analisi)...[/bold yellow]")
            
            # Eseguiamo il comando
            clean_response, report_filename = agent.run(user_input)
            
            if clean_response:
                console.print(Panel(
                    Markdown(clean_response), 
                    title="[bold green]Report di Mappatura e Analisi[/bold green]", 
                    border_style="green",
                    expand=False
                ))
                
                if report_filename:
                    console.print(f"[bold blue][+] Report salvato con successo in:[/bold blue] [underline]{report_filename}[/underline]\n")
            else:
                console.print("[bold red][-] Errore nell'elaborazione o risposta vuota.[/bold red]\n")
                
        except KeyboardInterrupt:
            console.print("\n\n[bold red][!] Interruzione forzata. Chiusura in corso...[/bold red]")
            break

if __name__ == "__main__":
    main()