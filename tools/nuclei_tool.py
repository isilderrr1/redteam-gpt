import subprocess
import json
from core.tools import BaseSecurityTool, ToolResult


class NucleiScannerTool(BaseSecurityTool):

    @property
    def name(self) -> str:
        return "Nuclei_Vulnerability_Scanner"

    @property
    def description(self) -> str:
        return (
            "Esegue una scansione di vulnerabilita' approfondita su un URL o IP. "
            "Usa questo strumento dopo Nmap su ogni URL presente in 'web_endpoints'. "
            "Trova CVE specifiche, misconfiguration, pannelli esposti e vulnerabilita' critiche."
        )

    def execute(self, target: str, **kwargs) -> ToolResult:
        try:
            scan_target = (
                target if target.startswith(("http://", "https://"))
                else f"http://{target}"
            )

            cmd = [
                "nuclei",
                "-u", scan_target,
                "-t", "cves,exposed-panels,misconfiguration,vulnerabilities",
                "-c", "25",
                "-timeout", "10",
                "-jsonl",
                "-silent",
                "-nc"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180
            )

            if not result.stdout.strip():
                return ToolResult(
                    success=True,
                    data={
                        "target": scan_target,
                        "message": (
                            "Nessuna vulnerabilita' rilevata dai template "
                            "cves/exposed-panels/misconfiguration/vulnerabilities."
                        ),
                        "count": 0
                    }
                )

            findings = []
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    severity = data.get("info", {}).get("severity", "unknown").lower()

                    finding = {
                        "id": data.get("template-id"),
                        "name": data.get("info", {}).get("name"),
                        "severity": severity,
                        "description": data.get("info", {}).get("description", "N/A"),
                        "matched_url": data.get("matched-at", scan_target),
                        "matcher": data.get("matcher-name", "N/A"),
                        "tags": data.get("info", {}).get("tags", [])
                    }
                    findings.append(finding)

                    if severity in severity_counts:
                        severity_counts[severity] += 1

                except json.JSONDecodeError:
                    continue

            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4, "unknown": 5}
            findings.sort(key=lambda x: severity_order.get(x["severity"], 5))

            return ToolResult(
                success=True,
                data={
                    "target": scan_target,
                    "count": len(findings),
                    "severity_summary": severity_counts,
                    "vulnerabilities": findings
                }
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                data={},
                error_message=(
                    f"Nuclei ha superato il timeout di 180 secondi su {target}. "
                    "Il server potrebbe star bloccando le scansioni o essere molto lento."
                )
            )
        except Exception as e:
            return ToolResult(success=False, data={}, error_message=str(e))