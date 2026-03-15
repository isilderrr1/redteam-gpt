# 🔴 RedTeam-GPT: Intelligence Offensiva Autonoma

[🇮🇹 Italiano](README.it.md) | [🇬🇧 English](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**RedTeam-GPT** è un framework autonomo di cybersecurity potenziato da Large Language Models (LLM), progettato per automatizzare la ricognizione, l'analisi delle vulnerabilità e la pianificazione degli attacchi. Utilizza l'orchestratore **LangGraph** e un framework **ReAct** (Reasoning and Acting) per gestire cicli decisionali complessi attraverso strumenti di sicurezza standard del settore.

---

## 🛠️ Ambiente e Architettura Avanzata

Il sistema si è evoluto da un semplice script a un motore di sicurezza modulare e all'avanguardia.

### 🧠 Motore di Intelligence e Memoria
* **LLM Core:** [DeepSeek-R1-14B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B), scelto per le sue avanzate capacità di ragionamento *Chain-of-Thought*.
* **Orchestrazione:** **LangGraph**. Gestisce lo stato dell'agente, permettendo cicli iterativi tra ragionamento ed esecuzione.
* **Memoria Attiva:** Implementazione di `MemorySaver`, che consente all'agente di mantenere il contesto dei risultati degli strumenti precedenti (ad esempio, ricordare i sottodomini scoperti durante le successive scansioni Nmap).
* **Integrità dei Dati:** Sviluppato con **Pydantic** (classe `ToolResult`) per garantire che l'IA riceva dati rigorosamente strutturati, riducendo drasticamente le allucinazioni.

### 🏗️ Design del Software
* **Strategy Pattern:** Ogni strumento di sicurezza è incapsulato in una classe dedicata che eredita da `BaseSecurityTool`, consentendo una modularità senza interruzioni.
* **Disaccoppiamento Pulito:** La logica è rigorosamente separata in `core/` (logica di base), `agents/` (logica IA) e `tools/` (integrazioni esterne).

---

## 🚀 La Toolchain Offensiva

L'agente adatta dinamicamente la sua strategia in base ai risultati, seguendo una metodologia offensiva professionale:

| Fase | Strumento | Funzione Strategica |
| :--- | :--- | :--- |
| **0. Recon** | **Subfinder** | Espansione della superficie di attacco tramite enumerazione dei sottodomini. |
| **1. Mapping** | **Nmap** | Identificazione delle porte, fingerprinting dei servizi e rilevamento del sistema operativo. |
| **2. Scanning** | **Nuclei** | Scansione delle vulnerabilità basata su template per CVE e configurazioni errate. |
| **3. Database** | **SQLMap** | Validazione automatizzata delle vulnerabilità SQL Injection (SQLi). |
| **4. Discovery** | **DirBuster** | Fuzzing per directory nascoste e file sensibili non indicizzati. |

---

## 🌟 Funzionalità Chiave

- **🤖 Workflow Autonomo Multi-Stadio:** L'agente può partire da un dominio radice, scoprire sottodomini, passare a IP specifici e lanciare exploit mirati senza intervento umano.
- **🎯 Reporting Markdown Adattivo:** I report vengono generati dinamicamente; l'IA dà priorità ai risultati critici, ai PoC (Proof-of-Concept) e ai passaggi di mitigazione basati sulla valutazione del rischio in tempo reale.
- **🛡️ Focus sulla Proof-of-Concept:** L'integrazione con Nuclei e SQLMap garantisce che i risultati siano supportati da prove, minimizzando significativamente i falsi positivi.
- **📟 UI Terminale Avanzata:** Sviluppata con la libreria `Rich`, include log di ragionamento in tempo reale, pannelli di stato e spinner interattivi.

---

## 📸 Demo Operativa

### 1. Interfaccia Utente del Terminale (TUI)
L'interfaccia mostra il ciclo **ReAct**. Puoi osservare l'IA mentre "pensa" (Chain-of-Thought) prima di decidere quale strumento specializzato invocare.

![Operational Dashboard](assets/TUI.png)

### 2. Report Autonomo del Percorso di Attacco
Al termine della sessione, un report Markdown professionale viene salvato nella cartella `reports/`, dettagliando la superficie di attacco scoperta e le correzioni di sicurezza raccomandate.

![Analysis Report](assets/report.png)

---

## 🔧 Installazione e Configurazione

1.  **Dipendenze di Sistema:**
    Assicurati di avere installato nel tuo PATH: `nmap`, `nuclei`, `subfinder`, `sqlmap`.

2.  **Clonazione e Setup:**
    ```bash
    git clone [https://github.com/isilderrr1/redteam-gpt.git](https://github.com/isilderrr1/redteam-gpt.git)
    cd redteam-gpt
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configurazione:**
    Configura il tuo file `.env` con l'URL della tua inferenza locale (es. LM Studio o Ollama).

4.  **Avvio:**
    ```bash
    python main.py
    ```

---

## ⚖️ Etica e Disclaimer
Questo progetto è solo a scopo **educativo e di ricerca**. L'uso di RedTeam-GPT contro bersagli senza previa autorizzazione scritta è illegale e non etico. L'autore non si assume alcuna responsabilità per eventuali danni derivanti dall'uso improprio di questo software.

**Sviluppato con 🔴 da Antonio Ruocco**