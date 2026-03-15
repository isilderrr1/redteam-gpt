import os
import re
import uuid
from datetime import datetime
from tools.nuclei_tool import NucleiScannerTool
from tools.sqlmap_tool import SQLMapScannerTool
from tools.subdomain_tool import SubdomainScannerTool
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver # <-- IMPORTIAMO LA MEMORIA
from langchain_core.tools import Tool

# Importiamo i tool
from tools.nmap_tool import NmapScannerTool
from tools.cve_tool import CveSearchTool
from tools.dirbuster_tool import WebDirBusterTool

load_dotenv()

class RedTeamAgent:
    def __init__(self):
        """Inizializza l'Agente RedTeam con il motore moderno LangGraph e Memoria."""
        
        # 1. IL CERVELLO
        self.llm = ChatOpenAI(
            base_url=os.getenv("LOCAL_LLM_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("LOCAL_LLM_MODEL"),
            temperature=0.1, 
            max_tokens=2000
        )
        
        # Istanze fisiche dei nostri tool
        nmap_tool = NmapScannerTool()
        cve_tool = CveSearchTool()
        dir_tool = WebDirBusterTool()
        nuclei_tool = NucleiScannerTool()
        sub_tool = SubdomainScannerTool()
        sql_tool = SQLMapScannerTool()
        
        # 2. I Tool
        self.tools = [
            Tool(
                name="Nmap_Port_Scanner",
                description="Indispensabile per la ricognizione iniziale. Identifica porte aperte e versioni dei servizi su un IP o dominio.",
                func=lambda q: str(nmap_tool.execute(target=q).model_dump())
            ),
            Tool(
                name="Nuclei_Vulnerability_Scanner",
                description="Lo strumento più potente per confermare vulnerabilità reali. Usalo su ogni URL o servizio web trovato per ottenere Proof-of-Concept (PoC).",
                func=lambda q: str(nuclei_tool.execute(target=q).model_dump())
            ),
            Tool(
                name="CVE_Vulnerability_Searcher",
                description="Cerca vulnerabilità note basandosi su nome e versione del software. Utile per servizi non-web (es. SSH, FTP, SMB).",
                func=lambda q: str(cve_tool.execute(software_query=q).model_dump())
            ),
            Tool(
                name="Web_Directory_Buster",
                description="Esegue il brute-force di directory e file nascosti. Usalo se Nuclei non trova nulla di ovvio ma il server web sembra interessante.",
                func=lambda q: str(dir_tool.execute(target_url=q).model_dump())
            ), # <--- AGGIUNTA QUESTA VIRGOLA
            Tool(
                name="Subdomain_Finder",
                description="Trova sottodomini per espandere il raggio d'azione. Passa il dominio (es. 'google.com').",
                func=lambda q: str(sub_tool.execute(domain=q).model_dump())
            ),
            Tool(
                name="SQLMap_Scanner",
                description="Esegue test di SQL Injection su URL con parametri. Passa l'URL completo (es. 'http://site.com?id=5').",
                func=lambda q: str(sql_tool.execute(target_url=q).model_dump())
            )
        ]
        
        # 3. IL SYSTEM PROMPT (Pulito)
        self.system_prompt = """
        Sei 'RedTeam-GPT', un Agente di Cybersecurity Offensiva specializzato in Penetration Testing.
        Il tuo obiettivo è mappare la superficie di attacco e identificare vulnerabilità reali.

        STRATEGIA OPERATIVA:
        - FASE ZERO: Se l'utente fornisce un dominio anziché un IP, usa Subdomain_Finder per mappare l'infrastruttura. Scegli poi i sottodomini più interessanti (es. quelli che contengono 'dev', 'test', 'api', 'vpn') per procedere con Nmap.
        - FASE DI RECOVERY: Inizia sempre con 'Nmap_Port_Scanner' per identificare porte e servizi attivi.
        - ANALISI WEB: Se identifichi servizi HTTP/HTTPS (porte 80, 443, 8080, ecc.), usa IMMEDIATAMENTE 'Nuclei_Vulnerability_Scanner'. 
           Nuclei è lo strumento primario per confermare vulnerabilità web con Proof-of-Concept.
        - ANALISI DATABASE (SQLi): Se identifichi URL con parametri query (es. '?id=', '?cat=') o se l'utente fornisce direttamente un URL di questo tipo, usa IMMEDIATAMENTE 'SQLMap_Scanner'. È fondamentale per confermare l'esposizione dei dati.
        - APPROFONDIMENTO: Usa 'CVE_Vulnerability_Searcher' per analizzare le versioni specifiche dei software trovati da Nmap che non sono web-based.
        - ESPLORAZIONE: Usa 'Web_Directory_Buster' per scoprire file o percorsi nascosti su server web sospetti.

        REGOLE:
        1. Sii estremamente tecnico e preciso.
        2. Priorità assoluta alla riduzione dei falsi positivi tramite l'uso di Nuclei e SQLMap.
        3. FIDUCIA NEL TARGET: Se l'utente fornisce un URL completo con parametri (?), esegui SQLMap_Scanner anche se Nmap indica che l'host è down. Molti target bloccano le scansioni di porte ma sono vulnerabili via HTTP.
        4. Rispondi sempre in Italiano.
        """
        
        # 4. LA MEMORIA E LA SESSIONE
        self.memory = MemorySaver()
        self.thread_id = str(uuid.uuid4()) # ID univoco per ricordare questa specifica conversazione
        self.is_first_run = True # Flag per evitare di duplicare il System Prompt
        
        # 5. IL CICLO REACT
        self.app = create_react_agent(
            self.llm, 
            self.tools,
            checkpointer=self.memory # Agganciamo fisicamente la RAM all'agente
        )

    def run(self, command: str):
        """Esegue un comando usando l'agente e mostra il flusso di pensieri."""
        
        # Gestione intelligente del System Prompt per non intasarne la memoria
        if self.is_first_run:
            messages = [
                SystemMessage(content=self.system_prompt),
                ("user", command)
            ]
            self.is_first_run = False
        else:
            messages = [("user", command)]
            
        inputs = {"messages": messages}
        
        # Diciamo a LangGraph quale "cassetto della memoria" aprire
        config = {"configurable": {"thread_id": self.thread_id}}
        
        final_response = ""
        
        try:
            # Leggiamo lo streaming, passando anche la 'config' per la memoria
            for step in self.app.stream(inputs, config=config, stream_mode="updates"):
                for node, values in step.items():
                    message = values["messages"][-1]
                    
                    if message.type == "ai" and message.tool_calls:
                        for tc in message.tool_calls:
                            print(f"  [>] L'AI ha deciso di usare lo strumento: {tc['name']}...")
                    
                    elif message.type == "tool":
                        print(f"  [<] Strumento completato. Dati JSON inviati al cervello.")
                    
                    elif message.type == "ai" and message.content:
                         final_response = message.content
                         
           # PULIZIA DELL'OUTPUT: Rimuove i tag <think>...</think>
            clean_response = re.sub(r'<think>.*?</think>', '', final_response, flags=re.DOTALL).strip()
            
            # --- MODIFICA CLEAN WORKSPACE ---
            # Crea la cartella 'reports' se non esiste già
            os.makedirs("reports", exist_ok=True)
            
            # GENERAZIONE AUTOMATICA DEL REPORT NELLA NUOVA CARTELLA
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"reports/attack_path_report_{timestamp}.md"
            
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(f"# 🔴 RedTeam-GPT: Attack Path Report\n")
                f.write(f"**Data e Ora:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Target/Comando:** `{command}`\n")
                f.write("---\n\n")
                f.write(clean_response)
            
            # Salva anche i log dei pensieri nel file nascosto dentro 'reports'
            with open("reports/.ai_thoughts.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- THOUGHT LOG ({timestamp}) ---\n{final_response}\n")
            # --------------------------------
                
            return clean_response, report_filename
            
        except Exception as e:
            return None, str(e)