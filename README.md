# 🔴 RedTeam-GPT: Autonomous Offensive Intelligence

[🇮🇹 Italiano](README.it.md) | [🇬🇧 English](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**RedTeam-GPT** is an autonomous cybersecurity agent powered by Large Language Models (LLMs), designed to automate reconnaissance, vulnerability analysis, and attack planning. It utilizes a **ReAct** (Reasoning and Acting) framework to interact with industry-standard security tools.

---

<<<<<<< HEAD
##  Ambiente di Sviluppo & Architettura
=======
## 🛠️ Development Environment & Architecture
>>>>>>> 357d975 (docs: add bilingual support (English/Italian))

The project was developed in a modern, high-performance ecosystem:
* **OS:** Ubuntu via WSL2 (Windows Subsystem for Linux).
* **IDE:** Visual Studio Code.
<<<<<<< HEAD
* **LLM Engine:** LM Studio / Ollama (Local Inference per la massima privacy).
* **Language:** Python 3.10+ con gestione ambienti virtuali (`venv`).
###  Intelligence Engine
Il cuore decisionale del sistema è alimentato da:
* **LLM:** [DeepSeek-R1-14B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B)
* **Inference Server:** LM Studio / Ollama.
* **Reasoning Model:** Il sistema sfrutta le capacità di *Chain-of-Thought* di DeepSeek per analizzare i risultati dei tool e pianificare i passi successivi in modo autonomo.
=======
* **LLM Engine:** LM Studio / Ollama (Local Inference for maximum privacy).
* **Language:** Python 3.10+ with virtual environment management (`venv`).
>>>>>>> 357d975 (docs: add bilingual support (English/Italian))

### 🧠 Intelligence Engine
The system's decision-making core is powered by:
* **LLM:** [DeepSeek-R1-14B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B)
* **Inference Server:** LM Studio / Ollama.
* **Reasoning Model:** The system leverages DeepSeek's *Chain-of-Thought* capabilities to analyze tool outputs and plan subsequent steps autonomously.

### Design & Scalability
Designed following **Object-Oriented Programming (OOP)** principles and the **Strategy** pattern:
* **Tool Modularity:** Every tool (Nmap, CVE Searcher, etc.) inherits from an abstract base class. Adding a new tool takes only minutes without touching the AI core.
* **Decoupling:** The User Interface (Rich UI) is separated from the agent's logic, allowing for future Web UI or API integration.
* **Memory & Context:** The agent maintains session history to "reason" over previous scan results.

---

<<<<<<< HEAD
##  Caratteristiche Principali
=======
## 🚀 Key Features
>>>>>>> 357d975 (docs: add bilingual support (English/Italian))

- **🤖 Autonomous Decision Making:** The AI doesn't follow a linear script; it decides which tool to use based on the received output.
- **🔍 Version Fingerprinting:** Using Nmap (`-sV`), the agent extracts exact service versions for pinpoint accuracy.
- **🛡️ CVE Integration:** Automated lookup for known vulnerabilities in the CVE database for every identified service.
- **📊 Professional Reporting:** Automatic generation of Markdown reports in the `reports/` folder.
- **📟 Advanced Terminal:** Eye-catching UI developed with the `Rich` library, featuring spinners, panels, and real-time logs.

---

<<<<<<< HEAD
##  Dimostrazione Operativa
=======
## 📸 Operational Demo
>>>>>>> 357d975 (docs: add bilingual support (English/Italian))

### 1. Terminal User Interface (TUI)
The main interface shows the agent in action. Once the target is set, the system initiates the **ReAct** reasoning cycle, displaying selected tools and the AI's decision-making process in real-time.

![Operational Dashboard](assets/TUI.png)

### 2. Final Report & Analysis
At the end of the session, RedTeam-GPT generates a summary report in the terminal and saves a detailed Markdown version. The report includes service mapping, identified vulnerabilities, and suggested attack paths.

![Analysis Report](assets/report.png)

---

## 🔧 How to Replicate

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/isilderrr1/redteam-gpt.git
    cd redteam-gpt
    ```
2.  **Setup the Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Environment Variables (.env):**
    Create a `.env` file and set your local inference URL (e.g., `http://localhost:1234/v1`).
4.  **Run:**
    ```bash
    python main.py
    ```

---

<<<<<<< HEAD
##  Etica e Disclaimer
Questo progetto è stato creato per scopi **puramente educativi** e per la ricerca sulla sicurezza informatica. L'utilizzo di RedTeam-GPT contro target senza previa autorizzazione scritta è illegale e immorale. L'autore non si assume alcuna responsabilità per danni derivanti dall'uso improprio di questo software.

**Developed  by Antonio Ruocco**
=======
## ⚖️ Ethics and Disclaimer
This project was created for **purely educational purposes** and cybersecurity research. Using RedTeam-GPT against targets without prior written authorization is illegal and unethical. The author assumes no responsibility for any damage resulting from the misuse of this software.

**Developed with 🔴 by Antonio Ruocco**
>>>>>>> 357d975 (docs: add bilingual support (English/Italian))
