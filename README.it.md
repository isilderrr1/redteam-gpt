# 🔴 RedTeam-GPT: Intelligence Offensiva Autonoma

[🇮🇹 Italiano](README.it.md) | [🇬🇧 English](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Model: Qwen2.5-14B](https://img.shields.io/badge/Model-Qwen2.5--14B-orange.svg)](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct)
[![LangGraph: ReAct](https://img.shields.io/badge/LangGraph-ReAct-blue.svg)](https://langchain-ai.github.io/langgraph/)

**RedTeam-GPT** è un framework autonomo di cybersecurity potenziato da Large Language Models (LLM), progettato per automatizzare la ricognizione passiva e attiva, l'analisi delle vulnerabilità e la pianificazione del percorso d'attacco. Utilizza l'orchestratore **LangGraph** con un loop **ReAct** (Reasoning and Acting) per gestire cicli decisionali complessi e multi-stadio attraverso strumenti di sicurezza offensiva standard del settore.

---

## 🛠️ Architettura

Il sistema si è evoluto da un semplice script a un motore di sicurezza offensiva modulare e production-grade.

### 🧠 Motore di Intelligence e Memoria

* **LLM Core:** [Qwen2.5-14B-Instruct](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct) — scelto per il suo **supporto nativo al tool calling**, ragionamento tecnico superiore e ottime prestazioni multilingua. Eseguito in locale tramite **LM Studio**.
* **Orchestrazione:** **LangGraph** `create_react_agent` con integrazione completa del tool calling. Gestisce cicli iterativi ragionamento/esecuzione con stato persistente.
* **Memoria Attiva:** Implementazione di `MemorySaver` — l'agente mantiene il contesto completo tra le chiamate ai tool all'interno di una sessione (es. i sottodomini trovati da Subfinder vengono ricordati quando viene invocato Nmap).
* **Integrità dei Dati:** Tutti gli output dei tool sono validati tramite **Pydantic** (classe `ToolResult`), garantendo che l'LLM riceva sempre dati rigorosamente strutturati e riducendo drasticamente le allucinazioni.
* **Input Routing:** Dispatcher personalizzato `_extract_input()` gestisce in modo trasparente tutti i formati di argomento di LangChain (`__arg1`, posizionale, keyword).

### 🏗️ Design del Software

* **Strategy Pattern:** Ogni tool di sicurezza eredita da `BaseSecurityTool` (`core/tools.py`), garantendo modularità ed estensibilità senza interruzioni.
* **Disaccoppiamento Pulito:** La logica è rigorosamente separata in `core/` (astrazioni base), `agents/` (orchestrazione IA) e `tools/` (integrazioni esterne).
* **Architettura a Callback:** `main.py` inietta callback `on_tool_call` / `on_tool_done` nel loop di esecuzione dell'agente per aggiornamenti Rich UI in tempo reale, senza accoppiare UI e logica di business.

---

## 🚀 La Toolchain Offensiva

L'agente seleziona e concatena autonomamente i tool in base ai risultati trovati, seguendo una metodologia professionale di penetration testing:

| Fase | Strumento | Funzione Strategica |
| :--- | :--- | :--- |
| **0. Recon Passiva** | **Subfinder** | Espansione della superficie di attacco tramite enumerazione dei sottodomini. Attivato per primo su input di tipo dominio. |
| **1. Mapping Attivo** | **Nmap** | Identificazione porte, fingerprinting servizi (version detection), scansione top-1000 porte con timeout 120s per host. Restituisce `web_endpoints` e `non_web_services` strutturati per i tool downstream. |
| **2. Web Scanning** | **Nuclei** | Scansione vulnerabilità basata su template (`cves`, `exposed-panels`, `misconfiguration`, `vulnerabilities`). Punta agli URL esatti con porte corrette dall'output di Nmap. Risultati ordinati per severity. |
| **3. CVE Lookup** | **NIST NVD** | Interroga le API NIST NVD v2 per CVE note sui servizi non-web trovati da Nmap. Restituisce CVSS score, severity label, vettore di attacco e data di pubblicazione. Filtra CVE con CVSS < 4.0. |
| **4. Directory Fuzzing** | **DirBuster** | Brute-force multi-thread di 50+ path comuni. Include confronto con baseline HTTP per filtrare 404 custom e analisi dei redirect per eliminare falsi positivi. |
| **5. SQL Injection** | **SQLMap** | Test SQLi automatizzato su URL con parametri e form di login. Estrae parametro vulnerabile, tipo di injection, DBMS e payload di esempio. Include rilevamento WAF. |

---

## 🌟 Funzionalità Chiave

- **🤖 Workflow Autonomo Multi-Stadio:** L'agente parte da un dominio o IP, esegue l'intera kill chain (recon → mapping → scanning → exploitation) e produce un report strutturato — zero intervento manuale.
- **🔧 Tool Calling Nativo:** Qwen2.5-14B supporta function calling compatibile OpenAI, garantendo invocazioni dei tool affidabili tramite LangGraph senza hack di parsing custom.
- **🛡️ Eliminazione Falsi Positivi:** DirBuster usa baseline HTTP e analisi dei redirect. Nuclei punta solo alle porte aperte confermate. I risultati CVE sono filtrati per soglia CVSS.
- **📊 Report Strutturato:** I report includono tabella porte Nmap, CVE confermate con CVSS score e vettori di attacco, finding Nuclei con URL colpito, e risultati DirBuster con status code.
- **💾 Salvataggio Report Opzionale:** Al termine di ogni analisi, l'agente chiede se salvare il report. I report salvati usano un template Markdown professionale con frontmatter YAML e classificazione di confidenzialità.
- **📟 UI Terminale Avanzata:** Costruita con `Rich` — icone specifiche per ogni tool, pannelli colorati, streaming in tempo reale delle chiamate ai tool, prompt di salvataggio interattivo e pannello report professionale.

---

## 🖥️ Requisiti Hardware

| Componente | Raccomandato | Minimo |
| :--- | :--- | :--- |
| **GPU VRAM** | 12 GB (RTX 4070+) | 8 GB |
| **RAM** | 16 GB | 12 GB |
| **LM Studio** | Ultima versione | 0.3.x+ |
| **Modello** | Qwen2.5-14B-Instruct Q4_K_M | Qwen2.5-7B-Instruct Q8 |

### Impostazioni LM Studio Consigliate

| Parametro | Valore |
| :--- | :--- |
| GPU Offload | 99 |
| Context Length | 16384 |
| Flash Attention | ON |
| Reasoning Parsing | ON (`<think>` / `</think>`) |
| Temperature | 0.1 |
| Structured Output | OFF |

---

## 🔧 Installazione e Configurazione

### 1. Dipendenze di Sistema

```bash
# Nmap
sudo apt install nmap

# Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
nuclei -update-templates

# Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# SQLMap
pip install sqlmap
```

### 2. Clonazione e Setup

```bash
git clone https://github.com/isilderrr1/redteam-gpt.git
cd redteam-gpt
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurazione

Crea un file `.env` nella root del progetto:

```dotenv
LOCAL_LLM_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
LOCAL_LLM_MODEL=qwen2.5-14b-instruct-1m
NIST_API_KEY=la_tua_chiave_nist_qui   # Opzionale — chiave gratuita su nvd.nist.gov
```

### 4. Avvio

```bash
python main.py
```

---

## 📁 Struttura del Progetto

```
redteam-gpt/
├── agents/
│   └── redteam_agent.py       # Agente LangGraph ReAct, system prompt, memoria
├── core/
│   └── tools.py               # BaseSecurityTool, ToolResult (Pydantic)
├── tools/
│   ├── nmap_tool.py           # Port scanner con output web_endpoints
│   ├── nuclei_tool.py         # Vulnerability scanner con ordinamento severity
│   ├── subdomain_tool.py      # Integrazione Subfinder
│   ├── dirbuster_tool.py      # Dir fuzzer multi-thread con filtro FP
│   ├── sqlmap_tool.py         # SQLi scanner con parsing output
│   └── cve_tool.py            # Integrazione API NIST NVD v2
├── reports/                   # Report attack path salvati (Markdown)
├── main.py                    # Rich TUI, callback routing, salvataggio report
├── requirements.txt
└── .env
```

---

## 🗺️ Roadmap

| Priorità | Feature | Descrizione |
| :--- | :--- | :--- |
| 🔴 Alta | **Shodan Recon** | Ricognizione passiva tramite API Shodan — ottieni porte, CVE storiche e certificati SSL senza inviare un singolo pacchetto al target |
| 🔴 Alta | **Human-in-the-Loop** | LangGraph Interrupt prima dei tool distruttivi (SQLMap high-risk, Hydra) — l'agente si mette in pausa e attende l'approvazione dell'operatore |
| 🔴 Alta | **WhatWeb Fingerprinter** | Rilevamento CMS e tecnologie per rendere la selezione dei template Nuclei chirurgica |
| 🟡 Media | **XSS Scanner** | Integrazione Dalfox per test di vulnerabilità lato client |
| 🟡 Media | **JS Analyzer** | LinkFinder per estrarre endpoint API nascosti dai file JavaScript |
| 🟡 Media | **Report HTML** | Report HTML interattivo con sezioni collassabili e grafici severity |
| 🟢 Bassa | **Hydra Bruteforce** | Test credenziali su SSH/FTP/SMB (richiede Human-in-Loop prima) |
| 🟢 Bassa | **Modalità Batch** | Accetta una lista di target da file e produce un report consolidato |
| 🟢 Bassa | **Storico Sessioni** | Database SQLite per tracciare i target nel tempo e rilevare nuove vulnerabilità |

---

## ⚖️ Etica e Disclaimer

Questo progetto è solo a scopo **educativo e di ricerca**. L'uso di RedTeam-GPT contro bersagli senza previa autorizzazione scritta esplicita è illegale e non etico. L'autore non si assume alcuna responsabilità per eventuali danni derivanti dall'uso improprio di questo software.

> **Ottieni sempre un'autorizzazione scritta prima di eseguire qualsiasi assessment di sicurezza.**

**Sviluppato con 🔴 da Antonio Ruocco**
