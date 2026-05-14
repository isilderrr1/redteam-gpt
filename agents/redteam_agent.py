import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import Tool

from tools.nmap_tool import NmapScannerTool
from tools.nuclei_tool import NucleiScannerTool
from tools.sqlmap_tool import SQLMapScannerTool
from tools.subdomain_tool import SubdomainScannerTool
from tools.cve_tool import CveSearchTool
from tools.dirbuster_tool import WebDirBusterTool

load_dotenv()


def _extract_input(args, kwargs, fallback_keys):
    """Estrae l'input corretto indipendentemente da come LangChain passa i parametri."""
    # Caso 1: passato come argomento posizionale
    if args:
        return args[0]
    # Caso 2: passato con il nome corretto
    for key in fallback_keys:
        if key in kwargs:
            return kwargs[key]
    # Caso 3: LangChain rinomina a __arg1
    if "__arg1" in kwargs:
        return kwargs["__arg1"]
    # Caso 4: primo valore disponibile
    if kwargs:
        return next(iter(kwargs.values()))
    return ""

def _make_nmap_func(tool):
    def fn(*args, **kwargs):
        q = _extract_input(args, kwargs, ["target", "q"])
        return str(tool.execute(target=q).model_dump())
    return fn

def _make_nuclei_func(tool):
    def fn(*args, **kwargs):
        q = _extract_input(args, kwargs, ["target", "q"])
        return str(tool.execute(target=q).model_dump())
    return fn

def _make_cve_func(tool):
    def fn(*args, **kwargs):
        q = _extract_input(args, kwargs, ["software_query", "q"])
        return str(tool.execute(software_query=q).model_dump())
    return fn

def _make_dir_func(tool):
    def fn(*args, **kwargs):
        q = _extract_input(args, kwargs, ["target_url", "q"])
        return str(tool.execute(target_url=q).model_dump())
    return fn

def _make_sub_func(tool):
    def fn(*args, **kwargs):
        q = _extract_input(args, kwargs, ["domain", "q"])
        return str(tool.execute(domain=q).model_dump())
    return fn

def _make_sql_func(tool):
    def fn(*args, **kwargs):
        q = _extract_input(args, kwargs, ["target_url", "q"])
        return str(tool.execute(target_url=q).model_dump())
    return fn


class RedTeamAgent:
    def __init__(self):
        """Inizializza l'Agente RedTeam con LangGraph e Memoria."""

        self.llm = ChatOpenAI(
            base_url=os.getenv("LOCAL_LLM_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("LOCAL_LLM_MODEL"),
            temperature=0.1,
            max_tokens=4096
        )

        # Istanze fisiche dei tool
        nmap_tool    = NmapScannerTool()
        nuclei_tool  = NucleiScannerTool()
        cve_tool     = CveSearchTool()
        dir_tool     = WebDirBusterTool()
        sub_tool     = SubdomainScannerTool()
        sql_tool     = SQLMapScannerTool()

        # Fix closure: ogni lambda è isolata nella propria factory function
        self.tools = [
            Tool(
                name="Nmap_Port_Scanner",
                description=(
                    "Indispensabile per la ricognizione iniziale. "
                    "Identifica porte aperte e versioni dei servizi su un IP o dominio. "
                    "Passa solo l'IP o il dominio come stringa (es. '192.168.1.1' o 'example.com')."
                ),
                func=_make_nmap_func(nmap_tool)
            ),
            Tool(
                name="Nuclei_Vulnerability_Scanner",
                description=(
                    "Lo strumento più potente per confermare vulnerabilità reali con Proof-of-Concept. "
                    "Usalo su ogni URL o servizio web trovato da Nmap (porte 80, 443, 8080, ecc.). "
                    "Passa l'URL completo (es. 'http://192.168.1.1') o solo l'IP."
                ),
                func=_make_nuclei_func(nuclei_tool)
            ),
            Tool(
                name="CVE_Vulnerability_Searcher",
                description=(
                    "Cerca vulnerabilità note (CVE) per nome e versione del software. "
                    "Usalo per servizi non-web trovati da Nmap (es. SSH, FTP, SMB). "
                    "Passa nome e versione (es. 'OpenSSH 7.4' o 'vsftpd 2.3.4')."
                ),
                func=_make_cve_func(cve_tool)
            ),
            Tool(
                name="Web_Directory_Buster",
                description=(
                    "Esegue brute-force di directory e file nascosti su un server web. "
                    "Usalo se Nuclei non trova nulla ma il server web sembra interessante. "
                    "Passa l'URL base (es. 'http://192.168.1.1')."
                ),
                func=_make_dir_func(dir_tool)
            ),
            Tool(
                name="Subdomain_Finder",
                description=(
                    "Trova sottodomini per espandere la superficie di attacco. "
                    "Usalo come PRIMO PASSO se l'utente fornisce un dominio (non un IP). "
                    "Passa solo il dominio radice (es. 'example.com')."
                ),
                func=_make_sub_func(sub_tool)
            ),
            Tool(
                name="SQLMap_Scanner",
                description=(
                    "Testa SQL Injection su URL con parametri query. "
                    "Usalo SOLO su URL che contengono parametri (es. 'http://site.com/page.php?id=1'). "
                    "Passa l'URL completo con i parametri."
                ),
                func=_make_sql_func(sql_tool)
            ),
        ]

        self.system_prompt = """Sei 'RedTeam-GPT', un agente di Penetration Testing autonomo e metodico.
Il tuo obiettivo e' mappare la superficie di attacco e identificare vulnerabilita' reali, seguendo una metodologia professionale.
 
FLUSSO OPERATIVO OBBLIGATORIO - RISPETTA SEMPRE QUESTO ORDINE:
1. PRIMO STEP SEMPRE OBBLIGATORIO: usa Nmap_Port_Scanner sul target. Passa SOLO l'host o IP puro, mai URL con http://. Nmap restituisce 'web_endpoints' (URL gia' pronti per Nuclei) e 'non_web_services' (query pronte per CVE).
2. Se l'input e' un DOMINIO → usa prima Subdomain_Finder, poi Nmap sui sottodomini piu' interessanti (dev, test, api, vpn, admin).
3. Per ogni URL nel campo 'web_endpoints' restituito da Nmap → usa Nuclei_Vulnerability_Scanner con quell'URL esatto (gia' include la porta corretta, es. http://host:8080).
4. Per ogni servizio in 'non_web_services' → usa CVE_Vulnerability_Searcher con il campo 'cve_query' esatto restituito da Nmap.
5. Se Nuclei non trova nulla → usa Web_Directory_Buster sull'URL base.
6. Se trovi URL con parametri query (?id=, ?cat=, ?page=) → usa SQLMap_Scanner.
 
REGOLE FERREE:
- Esegui SEMPRE almeno 2-3 tool prima di scrivere il report finale.
- Non inventare vulnerabilita': riporta SOLO cio' che i tool hanno confermato.
- Sii tecnico e preciso: includi porte, versioni, CVE ID, severity.
- Il report finale deve essere in Markdown strutturato con sezioni: Superficie di Attacco, Vulnerabilita' Confermate, Vettori di Attacco, Raccomandazioni.
- STRUTTURA REPORT OBBLIGATORIA — includi sempre tutte queste sezioni con i dati grezzi dei tool:
  * Superficie di Attacco: tabella con IP, porte aperte, servizio, versione esatta trovata da Nmap.
  * Vulnerabilita' Confermate: per ogni CVE includi ID (es. CVE-2024-XXXX), CVSS score, severity label, attack vector. Per Nuclei includi template-id, severity, URL colpito.
  * Vettori di Attacco: path trovati da DirBuster con status code, SQLi confermata con parametro e payload.
  * Raccomandazioni: azioni correttive specifiche basate sui risultati.
- Non omettere mai i dati grezzi dei tool anche se il risultato e' negativo: riporta comunque cosa e' stato testato e il responso.
- Rispondi sempre in Italiano."""


        self.memory = MemorySaver()
        self.thread_id = str(uuid.uuid4())
        self.is_first_run = True

        self.app = create_react_agent(
            self.llm,
            self.tools,
            checkpointer=self.memory
        )

    def run(self, command: str, on_tool_call=None, on_tool_done=None):
        """Esegue un comando usando l'agente ReAct con memoria."""

        if self.is_first_run:
            messages = [
                SystemMessage(content=self.system_prompt),
                ("user", command)
            ]
            self.is_first_run = False
        else:
            messages = [("user", command)]

        inputs = {"messages": messages}
        config = {"configurable": {"thread_id": self.thread_id}}


        final_response = ""

        try:
            for step in self.app.stream(inputs, config=config, stream_mode="updates"):
                for node, values in step.items():
                    message = values["messages"][-1]

                    if message.type == "ai" and message.tool_calls:
                        for tc in message.tool_calls:
                            if on_tool_call:
                                on_tool_call(tc['name'], str(tc['args']))
                            else:
                                print(f"  [>] Tool invocato: {tc['name']} | Input: {tc['args']}")

                    elif message.type == "tool":
                        if on_tool_done:
                            on_tool_done(message.name)
                        else:
                            print(f"  [<] Tool completato: {message.name}")

                    elif message.type == "ai" and message.content:
                        final_response = message.content

            import re
            clean_response = re.sub(r'<think>.*?</think>', '', final_response, flags=re.DOTALL).strip()

            # Log pensieri AI (sempre, silenzioso)
            os.makedirs("reports", exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open("reports/.ai_thoughts.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- THOUGHT LOG ({timestamp}) ---\n{final_response}\n")

            return clean_response, None

        except Exception as e:
            return None, str(e)