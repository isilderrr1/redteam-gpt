import subprocess
from core.tools import BaseSecurityTool, ToolResult  # <--- Questo è il percorso corretto

class SubdomainScannerTool(BaseSecurityTool):
    @property
    def name(self) -> str:
        return "Subdomain_Finder"

    @property
    def description(self) -> str:
        return (
            "Trova i sottodomini associati a un dominio principale (es. 'nmap.org'). "
            "Usalo come PRIMO PASSO se l'utente fornisce un dominio per scoprire "
            "altri server potenzialmente vulnerabili nella stessa rete."
        )

    def execute(self, domain: str, **kwargs) -> ToolResult:
        try:
            # -silent per avere solo la lista dei domini, -nc per niente colori
            cmd = ["subfinder", "-d", domain, "-silent", "-nc"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if not result.stdout.strip():
                return ToolResult(success=True, data={"subdomains": [], "message": "Nessun sottodominio pubblico trovato."})

            subdomains = result.stdout.splitlines()
            return ToolResult(success=True, data={"subdomains": subdomains, "count": len(subdomains)})

        except Exception as e:
            return ToolResult(success=False, data={}, error_message=str(e))