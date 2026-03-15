# 🔴 RedTeam-GPT: Autonomous Offensive Intelligence

[🇮🇹 Italiano](README.it.md) | [🇬🇧 English](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

**RedTeam-GPT** is an autonomous cybersecurity framework powered by Large Language Models (LLMs), designed to automate reconnaissance, vulnerability analysis, and attack planning. It utilizes the **LangGraph** orchestrator and a **ReAct** (Reasoning and Acting) framework to manage complex decision-making cycles with industry-standard security tools.

---

## 🛠️ Environment & Advanced Architecture

The system has evolved from a simple script into a modular, state-of-the-art security engine.

### 🧠 Intelligence & Memory Engine
* **Core LLM:** [DeepSeek-R1-14B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B), leveraged for its advanced *Chain-of-Thought* reasoning.
* **Orchestration:** **LangGraph**. Manages the agent's state, allowing for iterative loops between reasoning and execution.
* **Active Memory:** Integrated `MemorySaver` implementation, enabling the agent to retain context from previous tool outputs (e.g., remembering discovered subdomains during subsequent Nmap scans).
* **Data Integrity:** Built with **Pydantic** (`ToolResult` class) to ensure the AI receives strictly structured data, drastically reducing hallucinations.

### 🏗️ Software Design
* **Strategy Pattern:** Every security tool is encapsulated in a dedicated class inheriting from `BaseSecurityTool`, allowing for seamless modularity.
* **Clean Decoupling:** Logic is strictly separated into `core/` (base logic), `agents/` (AI logic), and `tools/` (external integrations).

---

## 🚀 The Offensive Toolchain

The agent dynamically adapts its strategy based on the findings, following an professional offensive methodology:

| Phase | Tool | Strategic Function |
| :--- | :--- | :--- |
| **0. Recon** | **Subfinder** | Attack surface expansion via subdomain enumeration. |
| **1. Mapping** | **Nmap** | Port identification, service fingerprinting, and OS detection. |
| **2. Scanning** | **Nuclei** | Template-based vulnerability scanning for CVEs and misconfigurations. |
| **3. Database** | **SQLMap** | Automated validation of SQL Injection (SQLi) vulnerabilities. |
| **4. Discovery** | **DirBuster** | Fuzzing for hidden directories and unindexed sensitive files. |

---

## 🌟 Key Features

- **🤖 Multi-Stage Autonomous Workflow:** The agent can start from a root domain, discover subdomains, pivot to specific IPs, and launch targeted exploits without human intervention.
- **🎯 Adaptive Markdown Reporting:** Reports are dynamically generated; the AI prioritizes critical findings, PoCs (Proof-of-Concept), and mitigation steps based on real-time risk assessment.
- **🛡️ Proof-of-Concept Focus:** Integration with Nuclei and SQLMap ensures that findings are backed by evidence, significantly minimizing false positives.
- **📟 Advanced Terminal UI:** Developed with the `Rich` library, featuring real-time reasoning logs, status panels, and interactive spinners.

---

## 📸 Operational Demo

### 1. Terminal User Interface (TUI)
The interface displays the **ReAct** cycle. You can watch the AI "think" (Chain-of-Thought) before deciding which specialized tool to invoke.

![Operational Dashboard](assets/TUI.png)

### 2. Autonomous Attack Path Report
At the end of the session, a professional Markdown report is saved in the `reports/` folder, detailing the discovered attack surface and recommended security fixes.

![Analysis Report](assets/report.png)

---

## 🔧 Installation & Setup

1.  **System Dependencies:**
    Ensure you have the following installed in your PATH: `nmap`, `nuclei`, `subfinder`, `sqlmap`.

2.  **Clone and Setup:**
    ```bash
    git clone [https://github.com/isilderrr1/redteam-gpt.git](https://github.com/isilderrr1/redteam-gpt.git)
    cd redteam-gpt
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    Configure your `.env` file with your local inference URL (e.g., LM Studio or Ollama).

4.  **Launch:**
    ```bash
    python main.py
    ```

---

## ⚖️ Ethics and Disclaimer
This project is for **educational and research purposes only**. Using RedTeam-GPT against targets without prior written authorization is illegal and unethical. The author assumes no responsibility for any damage resulting from the misuse of this software.

**Developed with 🔴 by Antonio Ruocco**