import requests
from core.tools import BaseSecurityTool, ToolResult

class CveSearchTool(BaseSecurityTool):
    """
    Strumento per cercare vulnerabilità note (CVE) relative a un software specifico.
    """
    
    @property
    def name(self) -> str:
        return "CVE_Vulnerability_Searcher"

    @property
    def description(self) -> str:
        return (
            "Usa questo strumento per cercare vulnerabilità note (CVE) in un software. "
            "Passa il nome e la versione del servizio (es. 'Apache 2.4.49') come parametro 'software_query'."
        )

    def execute(self, software_query: str, **kwargs) -> ToolResult:
        # Usiamo le API pubbliche del NIST NVD v2
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={software_query}&resultsPerPage=5"
        
        try:
            # Aggiungiamo un timeout per evitare che l'IA rimanga bloccata in attesa
            response = requests.get(url, timeout=10)
            
            if response.status_code == 403:
                return ToolResult(
                    success=False,
                    error_message="Rate limit delle API NIST raggiunto. Attendi qualche istante e riprova."
                )
                
            response.raise_for_status()
            data = response.json()
            
            vulnerabilities = data.get("vulnerabilities", [])
            
            if not vulnerabilities:
                return ToolResult(
                    success=True,
                    data={"query": software_query, "cve_found": []},
                    error_message=f"Nessuna CVE trovata per {software_query}. Il servizio potrebbe essere sicuro."
                )
            
            # Estraiamo i dati utili per l'IA in modo pulito
            parsed_cves = []
            for item in vulnerabilities:
                cve = item.get("cve", {})
                cve_id = cve.get("id", "Unknown")
                descriptions = cve.get("descriptions", [])
                
                # Prendiamo la descrizione in inglese
                desc_text = next((d["value"] for d in descriptions if d["lang"] == "en"), "Nessuna descrizione")
                
                # Cerchiamo il punteggio CVSS se disponibile (metrica di gravità)
                metrics = cve.get("metrics", {})
                cvss_score = "N/A"
                if "cvssMetricV31" in metrics:
                    cvss_score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
                elif "cvssMetricV2" in metrics:
                    cvss_score = metrics["cvssMetricV2"][0]["cvssData"]["baseScore"]

                parsed_cves.append({
                    "cve_id": cve_id,
                    "cvss_score": cvss_score,
                    "description": desc_text
                })
                
            return ToolResult(
                success=True,
                data={
                    "query": software_query,
                    "total_results": len(parsed_cves),
                    "cve_found": parsed_cves
                }
            )

        except requests.exceptions.Timeout:
            return ToolResult(
                success=False,
                error_message="Il database CVE (NIST) ha impiegato troppo tempo a rispondere (Timeout)."
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Errore inaspettato durante la ricerca CVE: {str(e)}"
            )