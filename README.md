# 🔴 RedTeam-GPT: Autonomous Offensive Intelligence

[🇮🇹 Italiano](README.it.md) | [🇬🇧 English](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Model: Qwen2.5-14B](https://img.shields.io/badge/Model-Qwen2.5--14B-orange.svg)](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct)
[![LangGraph: ReAct](https://img.shields.io/badge/LangGraph-ReAct-blue.svg)](https://langchain-ai.github.io/langgraph/)

**RedTeam-GPT** is an autonomous cybersecurity framework powered by Large Language Models (LLMs), designed to automate reconnaissance, vulnerability analysis, and attack path planning. It uses the **LangGraph** orchestrator with a **ReAct** (Reasoning and Acting) loop to manage complex multi-stage decision cycles through industry-standard offensive security tools.

---

## 🛠️ Architecture

The system has evolved from a simple script into a modular, production-grade offensive security engine.

### 🧠 Intelligence & Memory Engine

* **Core LLM:** [Qwen2.5-14B-Instruct](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct) — chosen for its **native tool calling support**, superior technical reasoning, and strong multilingual performance. Runs locally via **LM Studio**.
* **Orchestration:** **LangGraph** `create_react_agent` with full tool calling integration. Manages iterative reasoning/execution cycles with persistent state.
* **Active Memory:** `MemorySaver` implementation — the agent retains full context across tool calls within a session (e.g., subdomains found by Subfinder are remembered when Nmap is invoked).
* **Data Integrity:** All tool outputs are validated via **Pydantic** (`ToolResult` class), ensuring the LLM always receives strictly structured data and drastically reducing hallucinations.
* **Input Routing:** Custom `_extract_input()` dispatcher handles all LangChain argument formats (`__arg1`, positional, keyword) transparently.

### 🏗️ Software Design

* **Strategy Pattern:** Every security tool inherits from `BaseSecurityTool` (`core/tools.py`), enabling seamless modularity and extension.
* **Clean Decoupling:** Logic is strictly separated into `core/` (base abstractions), `agents/` (AI orchestration), and `tools/` (external integrations).
* **Callback Architecture:** `main.py` injects `on_tool_call` / `on_tool_done` callbacks into the agent's run loop for real-time Rich UI updates without coupling UI to business logic.

---

## 🚀 The Offensive Toolchain

The agent autonomously selects and chains tools based on findings, following a professional penetration testing methodology:

| Phase | Tool | Strategic Function |
| :--- | :--- | :--- |
| **0. Passive Recon** | **Subfinder** | Attack surface expansion via subdomain enumeration. Triggered first on domain inputs. |
| **1. Active Mapping** | **Nmap** | Port identification, service fingerprinting (version detection), top-1000 port scan with 120s host timeout. Returns structured `web_endpoints` and `non_web_services` for downstream tools. |
| **2. Web Scanning** | **Nuclei** | Template-based vulnerability scanning (`cves`, `exposed-panels`, `misconfiguration`, `vulnerabilities`). Targets exact URLs with correct ports from Nmap output. Results sorted by severity. |
| **3. CVE Lookup** | **NIST NVD** | Queries NIST NVD API v2 for known CVEs on non-web services found by Nmap. Returns CVSS score, severity label, attack vector, and publication date. Filters out CVSS < 4.0. |
| **4. Directory Fuzzing** | **DirBuster** | Multi-threaded brute-force of 50+ common paths. Includes baseline comparison to filter custom 404s and redirect analysis to eliminate false positives. |
| **5. SQL Injection** | **SQLMap** | Automated SQLi testing on parameterized URLs and login forms. Extracts vulnerable parameter, injection type, DBMS, and sample payload. WAF detection included. |

---

## 🌟 Key Features

- **🤖 Fully Autonomous Multi-Stage Workflow:** The agent starts from a domain or IP, runs the full kill chain (recon → mapping → scanning → exploitation), and produces a structured report — zero manual intervention.
- **🔧 Native Tool Calling:** Qwen2.5-14B supports OpenAI-compatible function calling, enabling reliable tool invocation via LangGraph without custom parsing hacks.
- **🛡️ False Positive Elimination:** DirBuster uses HTTP baseline comparison and redirect analysis. Nuclei targets only confirmed open ports. CVE results are filtered by CVSS threshold.
- **📊 Structured Reporting:** Reports include a Nmap port table, confirmed CVEs with CVSS scores and attack vectors, Nuclei findings with matched URLs, and DirBuster results with status codes.
- **💾 Optional Report Saving:** After each analysis, the agent asks whether to save the report. Saved reports use a professional Markdown template with YAML frontmatter and confidentiality classification.
- **📟 Advanced Terminal UI:** Built with `Rich` — tool-specific icons, colored panels, real-time streaming of tool calls, interactive save prompt, and a professional attack report panel.

---

## 🖥️ Hardware Requirements

| Component | Recommended | Minimum |
| :--- | :--- | :--- |
| **GPU VRAM** | 12 GB (RTX 4070+) | 8 GB |
| **RAM** | 16 GB | 12 GB |
| **LM Studio** | Latest | 0.3.x+ |
| **Model** | Qwen2.5-14B-Instruct Q4_K_M | Qwen2.5-7B-Instruct Q8 |

### Recommended LM Studio Settings

| Parameter | Value |
| :--- | :--- |
| GPU Offload | 99 |
| Context Length | 16384 |
| Flash Attention | ON |
| Reasoning Parsing | ON (`<think>` / `</think>`) |
| Temperature | 0.1 |
| Structured Output | OFF |

---

## 🔧 Installation & Setup

### 1. System Dependencies

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

### 2. Clone and Setup

```bash
git clone https://github.com/isilderrr1/redteam-gpt.git
cd redteam-gpt
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:

```dotenv
LOCAL_LLM_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
LOCAL_LLM_MODEL=qwen2.5-14b-instruct-1m
NIST_API_KEY=your_nist_api_key_here   # Optional — get free key at nvd.nist.gov
```

### 4. Launch

```bash
python main.py
```

---

## 📁 Project Structure

```
redteam-gpt/
├── agents/
│   └── redteam_agent.py       # LangGraph ReAct agent, system prompt, memory
├── core/
│   └── tools.py               # BaseSecurityTool, ToolResult (Pydantic)
├── tools/
│   ├── nmap_tool.py           # Port scanner with web_endpoints output
│   ├── nuclei_tool.py         # Vulnerability scanner with severity sorting
│   ├── subdomain_tool.py      # Subfinder integration
│   ├── dirbuster_tool.py      # Multi-threaded dir fuzzer with FP filtering
│   ├── sqlmap_tool.py         # SQLi scanner with output parsing
│   └── cve_tool.py            # NIST NVD API v2 integration
├── reports/                   # Saved attack path reports (Markdown)
├── main.py                    # Rich TUI, callback routing, report saving
├── requirements.txt
└── .env
```

---

## 🗺️ Roadmap

| Priority | Feature | Description |
| :--- | :--- | :--- |
| 🔴 High | **Shodan Recon** | Passive reconnaissance via Shodan API — get ports, CVEs, and SSL certs without touching the target |
| 🔴 High | **Human-in-the-Loop** | LangGraph Interrupt before destructive tools (SQLMap high-risk, Hydra) — agent pauses and waits for operator approval |
| 🔴 High | **WhatWeb Fingerprinter** | CMS and technology detection to make Nuclei template selection surgical |
| 🟡 Medium | **XSS Scanner** | Dalfox integration for client-side vulnerability testing |
| 🟡 Medium | **JS Analyzer** | LinkFinder to extract hidden API endpoints from JavaScript files |
| 🟡 Medium | **HTML Report** | Interactive HTML report with collapsible sections and severity charts |
| 🟢 Low | **Hydra Bruteforce** | Credential testing on SSH/FTP/SMB (requires Human-in-Loop first) |
| 🟢 Low | **Batch Mode** | Accept a target list file and produce a consolidated report |
| 🟢 Low | **Session History** | SQLite database to track targets over time and detect new vulnerabilities |

---

## ⚖️ Ethics & Disclaimer

This project is for **educational and research purposes only**. Using RedTeam-GPT against targets without explicit prior written authorization is illegal and unethical. The author assumes no responsibility for any damage resulting from misuse of this software.

> **Always obtain written authorization before running any security assessment.**

**Developed with 🔴 by Antonio Ruocco**
