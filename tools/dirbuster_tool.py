import requests
from core.tools import BaseSecurityTool, ToolResult

class WebDirBusterTool(BaseSecurityTool):
    """
    Strumento per scoprire percorsi nascosti o file sensibili su un server web.
    Usa una wordlist minimale per garantire tempi di risposta rapidi all'IA.
    """
    
    @property
    def name(self) -> str:
        return "Web_Directory_Buster"

    @property
    def description(self) -> str:
        return (
            "Usa questo strumento se Nmap ha trovato una porta web (80 o 443) aperta. "
            "Serve a scoprire percorsi nascosti, pannelli di admin o file sensibili. "
            "Passa l'URL base (es. 'http://192.168.1.10') come parametro 'target_url'."
        )

    def execute(self, target_url: str, **kwargs) -> ToolResult:
        # Pulizia dell'input: assicuriamoci che l'URL abbia http:// e non finisca con /
        if not target_url.startswith(("http://", "https://")):
            target_url = "http://" + target_url
        target_url = target_url.rstrip("/")

        # La nostra "wordlist" iper-concentrata
        common_paths = [
            "/admin", "/login", "/config.php", "/.env", 
            "/.git/config", "/backup.zip", "/robots.txt", "/api"
        ]

        discovered = []
        
        try:
            for path in common_paths:
                url_to_test = f"{target_url}{path}"
                try:
                    # allow_redirects=False ci permette di catturare i redirect (es. 301 verso una pagina di login)
                    response = requests.get(url_to_test, timeout=3, allow_redirects=False)
                    
                    # 200 = Trovato, 403 = Accesso Negato (ma esiste!), 301/302 = Redirect
                    if response.status_code in [200, 403, 301, 302]:
                        discovered.append({
                            "path": path,
                            "status_code": response.status_code,
                            "url": url_to_test
                        })
                except requests.exceptions.RequestException:
                    # Se un singolo test fallisce (es. timeout), ignoriamo e passiamo al prossimo
                    continue 

            return ToolResult(
                success=True,
                data={
                    "base_url": target_url,
                    "paths_tested": len(common_paths),
                    "discovered_paths": discovered
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Errore critico durante l'enumerazione web: {str(e)}"
            )