import os
import time
import requests
from core.tools import BaseSecurityTool, ToolResult

NIST_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

CVSS_LABELS = {
    range(0, 1):   "None",
    range(1, 4):   "Low",
    range(4, 7):   "Medium",
    range(7, 9):   "High",
    range(9, 11):  "Critical",
}

def _cvss_label(score) -> str:
    """Converte score numerico in label testuale."""
    try:
        s = int(float(score))
        for r, label in CVSS_LABELS.items():
            if s in r:
                return label
    except (ValueError, TypeError):
        pass
    return "Unknown"


def _extract_metrics(metrics: dict) -> dict:
    """Estrae CVSS score, vettore e severity da metriche NVD."""
    result = {
        "score": "N/A",
        "severity": "N/A",
        "vector": "N/A",
        "attack_vector": "N/A",
    }

    # Preferenza: V31 > V30 > V2
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if key in metrics:
            entry = metrics[key][0]
            cvss_data = entry.get("cvssData", {})
            score = cvss_data.get("baseScore", "N/A")
            result["score"] = score
            result["severity"] = _cvss_label(score)
            result["vector"] = cvss_data.get("vectorString", "N/A")

            # Estrai Attack Vector (Network = sfruttabile da remoto)
            av = cvss_data.get("attackVector") or cvss_data.get("accessVector", "N/A")
            result["attack_vector"] = av
            break

    return result


class CveSearchTool(BaseSecurityTool):

    @property
    def name(self) -> str:
        return "CVE_Vulnerability_Searcher"

    @property
    def description(self) -> str:
        return (
            "Cerca vulnerabilita' note (CVE) per nome e versione del software. "
            "Usalo per servizi non-web trovati da Nmap usando il campo 'cve_query'. "
            "Restituisce CVE ordinate per gravita' con score CVSS, vettore di attacco e data."
        )

    def _fetch(self, params: dict, headers: dict) -> requests.Response:
        """Esegue la richiesta con un retry automatico."""
        for attempt in range(2):
            try:
                response = requests.get(
                    NIST_API_URL,
                    params=params,
                    headers=headers,
                    timeout=20
                )
                return response
            except requests.exceptions.Timeout:
                if attempt == 0:
                    time.sleep(2)  # Aspetta 2s prima del retry
                    continue
                raise

    def execute(self, software_query: str, **kwargs) -> ToolResult:
        api_key = os.getenv("NIST_API_KEY")
        headers = {}
        if api_key:
            headers["apiKey"] = api_key

        params = {
            "keywordSearch": software_query,
            "resultsPerPage": 10,
            "startIndex": 0,
        }

        try:
            response = self._fetch(params, headers)

            if response.status_code == 403:
                return ToolResult(
                    success=False,
                    error_message="Rate limit NIST raggiunto o API Key non valida."
                )

            if response.status_code == 429:
                return ToolResult(
                    success=False,
                    error_message="Troppe richieste al NIST NVD. Attendi qualche secondo e riprova."
                )

            response.raise_for_status()
            data = response.json()

            vulnerabilities = data.get("vulnerabilities", [])
            total_available = data.get("totalResults", 0)

            if not vulnerabilities:
                return ToolResult(
                    success=True,
                    data={
                        "query": software_query,
                        "total_available": 0,
                        "cve_found": [],
                        "message": f"Nessuna CVE trovata per '{software_query}'."
                    }
                )

            parsed_cves = []
            for item in vulnerabilities:
                cve = item.get("cve", {})
                cve_id = cve.get("id", "Unknown")

                # Descrizione in inglese
                descriptions = cve.get("descriptions", [])
                desc_text = next(
                    (d["value"] for d in descriptions if d["lang"] == "en"),
                    "No description available."
                )

                # Metriche CVSS
                metrics = _extract_metrics(cve.get("metrics", {}))

                # Date
                published = cve.get("published", "N/A")[:10]  # Solo YYYY-MM-DD
                last_modified = cve.get("lastModified", "N/A")[:10]

                # References (max 2)
                refs = [
                    r.get("url", "")
                    for r in cve.get("references", [])[:2]
                ]

                # Filtra CVE senza score o con score basso (< 4.0)
                try:
                    if float(metrics["score"]) < 4.0:
                        continue
                except (ValueError, TypeError):
                    pass  # Se score N/A, includi comunque

                parsed_cves.append({
                    "cve_id": cve_id,
                    "cvss_score": metrics["score"],
                    "severity": metrics["severity"],
                    "attack_vector": metrics["attack_vector"],
                    "cvss_vector": metrics["vector"],
                    "published": published,
                    "last_modified": last_modified,
                    "description": desc_text[:300],  # Tronca descrizioni lunghissime
                    "references": refs,
                })

            # Ordina per CVSS score decrescente
            parsed_cves.sort(
                key=lambda x: float(x["cvss_score"]) if x["cvss_score"] != "N/A" else 0,
                reverse=True
            )

            # Statistiche per severity
            severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
            for cve in parsed_cves:
                sev = cve.get("severity", "Unknown")
                if sev in severity_counts:
                    severity_counts[sev] += 1

            return ToolResult(
                success=True,
                data={
                    "query": software_query,
                    "total_available": total_available,
                    "returned": len(parsed_cves),
                    "severity_summary": severity_counts,
                    "cve_found": parsed_cves
                }
            )

        except requests.exceptions.Timeout:
            return ToolResult(
                success=False,
                error_message="NIST NVD non ha risposto entro il timeout (20s x 2 tentativi)."
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Errore durante la ricerca CVE: {str(e)}"
            )