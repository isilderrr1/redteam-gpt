import subprocess
import json
from core.tools import BaseSecurityTool, ToolResult # <--- Questo dice a Python di partire dalla root

class NucleiScannerTool(BaseSecurityTool):
    """
    Integrazione di Nuclei Scanner per il rilevamento avanzato di vulnerabilità.
    """

    @property
    def name(self) -> str:
        return "Nuclei_Vulnerability_Scanner"

    @property
    def description(self) -> str:
        return (
            "Esegue una scansione di vulnerabilità approfondita su un URL o IP. "
            "Usa questo strumento dopo Nmap se trovi servizi web (HTTP/HTTPS) "
            "per trovare CVE specifiche, misconfigurations e pannelli esposti."
        )

    def execute(self, target: str, **kwargs) -> ToolResult:
        try:
            # Assicuriamoci che il target abbia un protocollo per Nuclei
            scan_target = target if target.startswith(("http://", "https://")) else f"http://{target}"

            # Comando: -jsonl per output strutturato, -silent per evitare banner
            cmd = ["nuclei", "-u", scan_target, "-jsonl", "-silent", "-nc"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)

            if not result.stdout.strip():
                return ToolResult(
                    success=True, 
                    data={"message": "Nessuna vulnerabilità rilevata da Nuclei."},
                    error_message=""
                )

            findings = []
            for line in result.stdout.splitlines():
                if line.strip():
                    data = json.loads(line)
                    findings.append({
                        "id": data.get("template-id"),
                        "name": data.get("info", {}).get("name"),
                        "severity": data.get("info", {}).get("severity"),
                        "description": data.get("info", {}).get("description", "N/A"),
                        "matcher": data.get("matcher-name", "N/A")
                    })

            return ToolResult(success=True, data={"vulnerabilities": findings}, error_message="")

        except Exception as e:
            return ToolResult(success=False, data={}, error_message=str(e))