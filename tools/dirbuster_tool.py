import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.tools import BaseSecurityTool, ToolResult

# Wordlist espansa e categorizzata
WORDLIST = [
    # Admin & Login
    "/admin", "/admin/", "/administrator", "/admin.php", "/admin.html",
    "/login", "/login.php", "/signin", "/dashboard",
    # File sensibili
    "/.env", "/.env.local", "/.env.backup",
    "/.git/config", "/.git/HEAD",
    "/config.php", "/config.yml", "/config.json",
    "/backup.zip", "/backup.tar.gz", "/dump.sql",
    "/web.config", "/settings.php",
    # Info & Debug
    "/robots.txt", "/sitemap.xml", "/crossdomain.xml",
    "/phpinfo.php", "/info.php", "/test.php",
    "/server-status", "/server-info",
    # API & Dev
    "/api", "/api/v1", "/api/v2", "/graphql",
    "/swagger", "/swagger-ui", "/swagger.json", "/openapi.json",
    "/actuator", "/actuator/health", "/actuator/env",
    # CMS comuni
    "/wp-admin", "/wp-login.php", "/wp-config.php",
    "/joomla", "/administrator/index.php",
    # Upload & Files
    "/uploads", "/files", "/static", "/assets",
    # Monitoring
    "/.well-known/security.txt",
]


def _is_false_positive(response, base_url: str) -> bool:
    """
    Determina se una risposta è un falso positivo.
    Casi comuni: redirect alla homepage, 404 custom con status 200.
    """
    # Caso 1: redirect verso la root o homepage → path non esiste realmente
    if response.status_code in (301, 302):
        location = response.headers.get("Location", "")
        # Se il redirect punta alla root o a un dominio diverso → falso positivo
        if location in ("/", base_url, base_url + "/"):
            return True
        # Se il redirect punta fuori dal dominio → falso positivo
        if location.startswith("http") and base_url not in location:
            return True

    # Caso 2: risposta 200 ma body quasi vuoto → probabilmente 404 custom
    if response.status_code == 200:
        content_length = len(response.content)
        if content_length < 50:  # Body troppo piccolo per essere una pagina reale
            return True

    return False


def _check_path(base_url: str, path: str, baseline_length: int) -> dict | None:
    """Testa un singolo path e restituisce il risultato o None se falso positivo."""
    url = f"{base_url}{path}"
    try:
        response = requests.get(
            url,
            timeout=4,
            allow_redirects=False,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SecurityScanner/1.0)"}
        )

        # Filtra status non interessanti
        if response.status_code not in (200, 204, 301, 302, 307, 308, 403, 401, 405):
            return None

        # Filtra falsi positivi
        if _is_false_positive(response, base_url):
            return None

        # Filtra pagine con body identico alla homepage (404 custom con status 200)
        if response.status_code == 200 and baseline_length > 0:
            diff = abs(len(response.content) - baseline_length)
            if diff < 100:  # Body quasi identico alla homepage → 404 custom
                return None

        # Estrai header informativi
        interesting_headers = {}
        for h in ("Server", "X-Powered-By", "X-Generator", "Content-Type", "WWW-Authenticate"):
            if h in response.headers:
                interesting_headers[h] = response.headers[h]

        # Descrizione human-readable dello status
        status_meaning = {
            200: "TROVATO",
            204: "TROVATO (no content)",
            301: "REDIRECT PERMANENTE",
            302: "REDIRECT TEMPORANEO",
            307: "REDIRECT TEMPORANEO",
            308: "REDIRECT PERMANENTE",
            403: "ACCESSO NEGATO (esiste!)",
            401: "AUTENTICAZIONE RICHIESTA (esiste!)",
            405: "METODO NON CONSENTITO (esiste!)",
        }.get(response.status_code, str(response.status_code))

        result = {
            "path": path,
            "url": url,
            "status_code": response.status_code,
            "status_meaning": status_meaning,
            "content_length": len(response.content),
            "headers": interesting_headers,
        }

        # Aggiungi redirect destination se applicabile
        if response.status_code in (301, 302, 307, 308):
            result["redirect_to"] = response.headers.get("Location", "N/A")

        return result

    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None


class WebDirBusterTool(BaseSecurityTool):

    @property
    def name(self) -> str:
        return "Web_Directory_Buster"

    @property
    def description(self) -> str:
        return (
            "Esegue brute-force di directory e file nascosti su un server web. "
            "Usalo se Nuclei non trova nulla ma il web server sembra interessante. "
            "Passa l'URL base (es. 'http://192.168.1.10' o 'https://example.com')."
        )

    def execute(self, target_url: str, **kwargs) -> ToolResult:
        # Pulizia input
        if not target_url.startswith(("http://", "https://")):
            target_url = "http://" + target_url
        target_url = target_url.rstrip("/")

        try:
            # Step 1: richiesta baseline alla homepage per rilevare 404 custom
            baseline_length = 0
            try:
                baseline = requests.get(
                    target_url,
                    timeout=5,
                    allow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; SecurityScanner/1.0)"}
                )
                baseline_length = len(baseline.content)
            except requests.exceptions.RequestException:
                pass  # Se la homepage non risponde, procediamo senza baseline

            # Step 2: test concorrente dei path
            discovered = []

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(_check_path, target_url, path, baseline_length): path
                    for path in WORDLIST
                }
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        discovered.append(result)

            # Ordina per status code: 200 prima, poi 401/403, poi redirect
            priority = {200: 0, 204: 1, 401: 2, 403: 3, 405: 4, 301: 5, 302: 6, 307: 7, 308: 8}
            discovered.sort(key=lambda x: priority.get(x["status_code"], 9))

            return ToolResult(
                success=True,
                data={
                    "base_url": target_url,
                    "paths_tested": len(WORDLIST),
                    "discovered_count": len(discovered),
                    "baseline_size": baseline_length,
                    "discovered_paths": discovered
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Errore critico durante l'enumerazione web: {str(e)}"
            )