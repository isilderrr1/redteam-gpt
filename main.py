from agents.redteam_agent import RedTeamAgent
import requests
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.table import Table
from rich.live import Live
from rich import box
from rich.rule import Rule
from rich.style import Style
import time

console = Console()

def print_header():
    header_text = """
    ██████╗ ███████╗██████╗ ████████╗███████╗ █████╗ ███╗   ███╗      ██████╗ ██████╗ ████████╗
    ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗████╗ ████║     ██╔════╝ ██╔══██╗╚══██╔══╝
    ██████╔╝█████╗  ██║  ██║   ██║   █████╗  ███████║██╔████╔██║ ███╗██║  ███╗██████╔╝   ██║   
    ██╔══██╗██╔══╝  ██║  ██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║ ╚══╝██║   ██║██╔═══╝    ██║   
    ██║  ██║███████╗██████╔╝   ██║   ███████╗██║  ██║██║ ╚═╝ ██║     ╚██████╔╝██║        ██║   
    ╚═╝  ╚═╝╚══════╝╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝      ╚═════╝ ╚═╝        ╚═╝   
    """
    console.print(Panel(
        Text(header_text, style="bold red", justify="center"),
        title="[bold white]◈  Terminale Offensivo Autonomo  ◈[/bold white]",
        subtitle="[dim]Powered by Qwen2.5-14B · LangGraph ReAct · LM Studio[/dim]",
        border_style="red",
        padding=(0, 2),
    ))
    console.print()

def print_tool_call(tool_name: str, tool_input: str):
    """Stampa una riga stilizzata per ogni tool invocato."""
    icons = {
        "Nmap_Port_Scanner":           "🔍",
        "Nuclei_Vulnerability_Scanner": "☢️ ",
        "Web_Directory_Buster":        "📂",
        "SQLMap_Scanner":              "💉",
        "CVE_Vulnerability_Searcher":  "🗄️ ",
        "Subdomain_Finder":            "🌐",
    }
    icon = icons.get(tool_name, "⚙️ ")
    console.print(f"  {icon} [bold cyan]{tool_name}[/bold cyan] [dim]→[/dim] [yellow]{tool_input}[/yellow]")

def print_tool_done(tool_name: str):
    """Stampa conferma completamento tool."""
    console.print(f"  [bold green]✔[/bold green] [dim]{tool_name} completato[/dim]")

def check_llm_server():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("LOCAL_LLM_URL")
    if not url:
        return False
    try:
        requests.get(f"{url}/models", timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False

def ask_save_report(clean_response: str, command: str) -> str | None:
    """Chiede all'utente se vuole salvare il report e restituisce il filename o None."""
    console.print()
    console.print(Rule("[dim]Salvataggio Report[/dim]", style="dim"))

    save = Confirm.ask(
        "  [bold yellow]?[/bold yellow] Vuoi salvare il report su file?",
        default=True
    )

    if not save:
        console.print("  [dim]Report non salvato.[/dim]\n")
        return None

    from datetime import datetime
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"reports/report_{timestamp}.md"

    # Template professionale
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: RedTeam-GPT Attack Path Report\n")
        f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"target: {command}\n")
        f.write(f"tool: RedTeam-GPT · Qwen2.5-14B · LangGraph\n")
        f.write("classification: CONFIDENTIAL — Solo uso autorizzato\n")
        f.write("---\n\n")
        f.write("# 🔴 RedTeam-GPT — Attack Path Report\n\n")
        f.write(f"> **Target:** `{command}`  \n")
        f.write(f"> **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  \n")
        f.write(f"> **Classificazione:** CONFIDENTIAL  \n\n")
        f.write("---\n\n")
        f.write(clean_response)
        f.write("\n\n---\n")
        f.write("*Report generato automaticamente da RedTeam-GPT.*  \n")
        f.write("*L'uso di questo report è consentito solo su sistemi autorizzati.*\n")

    console.print(f"  [bold green]✔[/bold green] Report salvato in: [underline bold]{report_filename}[/underline bold]\n")
    return report_filename

def main():
    print_header()

    with console.status("[bold yellow]  Controllo connessione al server LLM...[/bold yellow]", spinner="dots"):
        if not check_llm_server():
            console.print(Panel(
                "[bold red]Server LLM non raggiungibile.[/bold red]\n"
                "[yellow]Assicurati che LM Studio sia avviato e verifica LOCAL_LLM_URL nel file .env[/yellow]",
                title="[red]✘ Errore Critico[/red]",
                border_style="red"
            ))
            return

    with console.status("[bold green]  Inizializzazione motore AI e caricamento strumenti...[/bold green]", spinner="bouncingBar"):
        agent = RedTeamAgent()
        time.sleep(0.5)

    console.print(Panel(
        "[bold green]Sistema operativo.[/bold green] Tutti i moduli caricati con successo.\n"
        "[dim]Strumenti attivi: Nmap · Nuclei · DirBuster · SQLMap · CVE · Subfinder[/dim]",
        title="[bold green]✔ Online[/bold green]",
        border_style="green",
        padding=(0, 2),
    ))
    console.print("[dim]  Digita un target o un comando. Usa 'esci' per terminare.[/dim]\n")

    while True:
        try:
            console.print(Rule(style="dim red"))
            user_input = console.input("\n[bold red]▶[/bold red] [bold white]Comando[/bold white] [dim]>[/dim] ")

            if user_input.lower() in ['exit', 'quit', 'esci']:
                console.print("\n[bold red]◈ Disconnessione. Sessione terminata.[/bold red]\n")
                break

            if not user_input.strip():
                continue

            console.print()
            console.print(Panel(
                f"[bold]Target:[/bold] [cyan]{user_input}[/cyan]",
                title="[yellow]⚡ Analisi in corso[/yellow]",
                border_style="yellow",
                padding=(0, 2),
            ))
            console.print()

            # Streaming con log tool
            clean_response, error = agent.run(
                user_input,
                on_tool_call=print_tool_call,
                on_tool_done=print_tool_done
            )

            if not clean_response:
                console.print(Panel(
                    f"[red]Errore durante l'elaborazione:[/red]\n{error}",
                    title="[red]✘ Errore[/red]",
                    border_style="red"
                ))
                continue

            # Report panel professionale
            console.print()
            console.print(Panel(
                Markdown(clean_response),
                title="[bold white on red]  🔴 ATTACK PATH REPORT  [/bold white on red]",
                subtitle=f"[dim]Target: {user_input}[/dim]",
                border_style="red",
                padding=(1, 2),
                expand=False,
            ))

            # Chiedi se salvare
            ask_save_report(clean_response, user_input)

        except KeyboardInterrupt:
            console.print("\n\n[bold red]◈ Interruzione forzata. Chiusura in corso...[/bold red]\n")
            break

if __name__ == "__main__":
    main()