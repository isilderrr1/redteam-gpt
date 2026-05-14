import re
import subprocess
from core.tools import BaseSecurityTool, ToolResult


VULN_PATTERNS = {
    "parameter":   re.compile(r"Parameter:\s+(.+?)\s+\(", re.IGNORECASE),
    "type":        re.compile(r"Type:\s+(.+)", re.IGNORECASE),
    "payload":     re.compile(r"Payload:\s+(.+)", re.IGNORECASE),
    "dbms":        re.compile(r"back-end DBMS:\s+(.+)", re.IGNORECASE),
    "os":          re.compile(r"operating system:\s+(.+)", re.IGNORECASE),
    "waf":         re.compile(r"WAF/IPS identified as\s+(.+)", re.IGNORECASE),
}


def _parse_sqlmap_output(output: str) -> dict:
    parsed = {
        "vulnerable_parameters": [],
        "injection_types": [],
        "payloads": [],
        "dbms": None,
        "os": None,
        "waf_detected": None,
    }
    for line in output.splitlines():
        line = line.strip()
        m = VULN_PATTERNS["parameter"].search(line)
        if m and m.group(1) not in parsed["vulnerable_parameters"]:
            parsed["vulnerable_parameters"].append(m.group(1).strip())
        m = VULN_PATTERNS["type"].search(line)
        if m and m.group(1) not in parsed["injection_types"]:
            parsed["injection_types"].append(m.group(1).strip())
        m = VULN_PATTERNS["payload"].search(line)
        if m and m.group(1) not in parsed["payloads"]:
            parsed["payloads"].append(m.group(1).strip())
        m = VULN_PATTERNS["dbms"].search(line)
        if m:
            parsed["dbms"] = m.group(1).strip()
        m = VULN_PATTERNS["os"].search(line)
        if m:
            parsed["os"] = m.group(1).strip()
        m = VULN_PATTERNS["waf"].search(line)
        if m:
            parsed["waf_detected"] = m.group(1).strip()
    return parsed


class SQLMapScannerTool(BaseSecurityTool):

    @property
    def name(self) -> str:
        return "SQLMap_Scanner"

    @property
    def description(self) -> str:
        return (
            "Testa SQL Injection su URL con parametri query o su pagine con form di login. "
            "Usalo su URL con parametri (es. 'http://site.com/page?id=1') "
            "o su URL di pannelli admin/login (es. 'http://site.com/admin'). "
            "Restituisce parametri vulnerabili, tipo di injection e database rilevato."
        )

    def execute(self, target_url: str, **kwargs) -> ToolResult:
        try:
            # Determina se l'URL ha gia' parametri query
            has_params = "?" in target_url

            cmd = [
                "sqlmap",
                "-u", target_url,
                "--batch",          # Nessuna interazione — risponde Y a tutto
                "--random-agent",   # User-agent casuale
                "--level=2",
                "--risk=2",
                "--timeout=10",
                "--retries=1",
                "--threads=3",
            ]

            # Aggiunge --forms solo se NON ci sono gia' parametri nell'URL
            # (--forms + --crawl causano prompt interattivi anche con --batch)
            if not has_params:
                cmd += ["--forms"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,
                input=""   # stdin vuoto: evita qualsiasi prompt interattivo
            )

            output = result.stdout + result.stderr

            vuln_keywords = [
                "is vulnerable",
                "parameter appears to be",
                "appears to be injectable",
                "sqlmap identified the following injection",
                "confirming",
            ]
            is_vulnerable = any(kw in output.lower() for kw in vuln_keywords)

            waf_detected = (
                "waf/ips" in output.lower() or
                "protection" in output.lower()
            )

            connection_refused = "connection refused" in output.lower()

            if connection_refused and not is_vulnerable:
                return ToolResult(
                    success=False,
                    data={"target": target_url},
                    error_message=(
                        "Il server ha rifiutato le connessioni di SQLMap. "
                        "Il target potrebbe avere un WAF o bloccare scanner automatici."
                    )
                )

            if is_vulnerable:
                details = _parse_sqlmap_output(output)
                return ToolResult(
                    success=True,
                    data={
                        "vulnerable": True,
                        "target": target_url,
                        "vulnerable_parameters": details["vulnerable_parameters"],
                        "injection_types": details["injection_types"],
                        "sample_payloads": details["payloads"][:3],
                        "dbms": details["dbms"],
                        "os": details["os"],
                        "waf_detected": details["waf_detected"],
                        "severity": "CRITICA",
                        "details": "SQL Injection CONFERMATA — accesso al database possibile."
                    }
                )

            return ToolResult(
                success=True,
                data={
                    "vulnerable": False,
                    "target": target_url,
                    "waf_detected": waf_detected,
                    "message": (
                        "Nessuna SQL Injection rilevata. "
                        + ("WAF/IPS rilevato — potrebbe bloccare i payload." if waf_detected else "")
                    )
                }
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                data={},
                error_message=(
                    f"SQLMap ha superato il timeout di 180 secondi su {target_url}."
                )
            )
        except Exception as e:
            return ToolResult(success=False, data={}, error_message=str(e))