import nmap
from core.tools import BaseSecurityTool, ToolResult

class NmapScannerTool(BaseSecurityTool):
    """
    Strumento concreto che esegue una scansione di rete su un target.
    L'LLM userà questa classe per scoprire le porte aperte e le VERSIONI dei servizi.
    """
    
    @property
    def name(self) -> str:
        return "Nmap_Port_Scanner"

    @property
    def description(self) -> str:
        return (
            "Usa questo strumento per scansionare un indirizzo IP o un dominio "
            "e scoprire quali porte e servizi sono aperti, includendo le versioni esatte del software. "
            "Devi passare l'IP come parametro 'target'."
        )

    def execute(self, target: str, **kwargs) -> ToolResult:
        scanner = nmap.PortScanner()
        try:
            # IL FIX E' QUI: Aggiunto -sV per il version fingerprinting. 
            # -F (Fast) lo rende rapido testando solo le top 100 porte.
            scanner.scan(target, arguments='-sV -T4 -F')
            
            # Preleviamo la lista degli host che Nmap ha effettivamente scansionato
            hosts = scanner.all_hosts()
            
            if not hosts:
                return ToolResult(
                    success=False, 
                    error_message=f"Host {target} non raggiungibile o protetto da firewall rigoroso."
                )

            # Prendiamo il primo host reale (l'IP risolto)
            scanned_host = hosts[0]

            # Estrazione pulita dei dati con VERSIONI
            open_ports = []
            for protocol in scanner[scanned_host].all_protocols():
                ports = scanner[scanned_host][protocol].keys()
                for port in ports:
                    port_data = scanner[scanned_host][protocol][port]
                    state = port_data['state']
                    service = port_data['name']
                    
                    # Estraiamo i dettagli della versione
                    product = port_data.get('product', '')
                    version = port_data.get('version', '')
                    extrainfo = port_data.get('extrainfo', '')
                    
                    # Formattiamo una stringa di versione pulita
                    full_version_string = f"{product} {version} {extrainfo}".strip()
                    if not full_version_string:
                        full_version_string = "Versione sconosciuta"
                        
                    if state == 'open':
                        open_ports.append({
                            "port": port, 
                            "protocol": protocol, 
                            "service": service,
                            "version": full_version_string  # <-- IL NUOVO DATO LETALE
                        })

            return ToolResult(
                success=True,
                data={
                    "original_target": target, 
                    "resolved_ip": scanned_host, 
                    "open_ports": open_ports
                }
            )

        except nmap.PortScannerError as e:
             return ToolResult(
                success=False,
                error_message=f"Errore di Nmap (possibili permessi mancanti): {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Errore critico inaspettato durante la scansione: {str(e)}"
            )