import subprocess
from core.tools import BaseSecurityTool, ToolResult

class SQLMapScannerTool(BaseSecurityTool):
    @property
    def name(self) -> str:
        return "SQLMap_Scanner"

    @property
    def description(self) -> str:
        return (
            "Testa vulnerabilità SQL Injection su URL con parametri (es. 'http://target.com/page.php?id=1'). "
            "Usa questo strumento SOLO se trovi URL con parametri query (?). "
            "È fondamentale per confermare se un attaccante può leggere i dati del database."
        )

    def execute(self, target_url: str, **kwargs) -> ToolResult:
        try:
            # --batch: non chiede conferme
            # --random-agent: simula un browser reale
            # --level=1 --risk=1: test rapidi e poco invasivi
            cmd = ["sqlmap", "-u", target_url, "--batch", "--random-agent", "--level=1", "--risk=1"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout
            
            # Verifichiamo se SQLMap ha trovato qualcosa di interessante
            is_vulnerable = "is vulnerable" in output.lower() or "confirming" in output.lower()
            
            if is_vulnerable:
                return ToolResult(
                    success=True, 
                    data={"vulnerable": True, "details": "SQL Injection CONFERMATA!", "raw_summary": "Il parametro analizzato è vulnerabile."},
                    error_message=""
                )
            
            return ToolResult(
                success=True, 
                data={"vulnerable": False, "message": "Nessuna SQL Injection rilevata con i test di base."},
                error_message=""
            )

        except Exception as e:
            return ToolResult(success=False, data={}, error_message=str(e))