import nmap
from core.tools import BaseSecurityTool, ToolResult

# Porte e servizi classificati come "web" -> Nuclei li scannerizzerà
WEB_SERVICES = {
    "http", "https", "http-alt", "https-alt",
    "http-proxy", "ssl/http", "ssl/https", "tomcat"
}

WEB_PORTS = {80, 443, 8080, 8443, 8000, 8888, 3000, 5000, 9090, 9443}


class NmapScannerTool(BaseSecurityTool):

    @property
    def name(self) -> str:
        return "Nmap_Port_Scanner"

    @property
    def description(self) -> str:
        return (
            "Scansiona un IP o dominio per identificare porte aperte, versioni dei servizi "
            "e sistema operativo. Restituisce anche gli URL web pronti per Nuclei. "
            "Passa solo l'IP o il dominio come stringa (es. '192.168.1.1' o 'example.com'). "
            "NON passare URL con http:// — solo host o IP puri."
        )

    def execute(self, target: str, **kwargs) -> ToolResult:

        # Pulizia input: rimuove http:// o https:// se l'utente li passa per errore
        clean_target = target.strip()
        for prefix in ("https://", "http://"):
            if clean_target.startswith(prefix):
                clean_target = clean_target[len(prefix):]
        clean_target = clean_target.rstrip("/")

        scanner = nmap.PortScanner()
        try:
            # -sV: version fingerprinting
            # -T4: velocità aggressiva
            # --top-ports 1000: top 1000 porte (più copertura di -F)
            # --host-timeout 120s: non bloccarsi su host lenti
            # -O: OS detection (richiede sudo, fallback graceful se non disponibile)
            scanner.scan(
                clean_target,
                arguments="-sV -T4 --top-ports 1000 --host-timeout 120s"
            )

            hosts = scanner.all_hosts()

            if not hosts:
                return ToolResult(
                    success=False,
                    error_message=(
                        f"Host '{clean_target}' non raggiungibile o tutti i port filtrati. "
                        "Potrebbe essere protetto da firewall."
                    )
                )

            scanned_host = hosts[0]
            host_info = scanner[scanned_host]

            # --- OS Detection (best effort) ---
            os_info = "Non rilevato"
            if "osmatch" in host_info and host_info["osmatch"]:
                best_match = host_info["osmatch"][0]
                os_info = f"{best_match['name']} (accuratezza: {best_match['accuracy']}%)"

            # --- Parsing porte ---
            open_ports = []
            web_urls = []      # URL pronti per Nuclei
            non_web_services = []  # Servizi per CVE lookup

            for protocol in host_info.all_protocols():
                for port in sorted(host_info[protocol].keys()):
                    port_data = host_info[protocol][port]

                    if port_data["state"] != "open":
                        continue

                    service  = port_data.get("name", "unknown")
                    product  = port_data.get("product", "")
                    version  = port_data.get("version", "")
                    extrainfo = port_data.get("extrainfo", "")

                    version_string = " ".join(
                        filter(None, [product, version, extrainfo])
                    ).strip() or "Versione sconosciuta"

                    port_entry = {
                        "port": port,
                        "protocol": protocol,
                        "service": service,
                        "version": version_string,
                    }
                    open_ports.append(port_entry)

                    # Classifica come web o non-web
                    is_web = (
                        service.lower() in WEB_SERVICES or
                        port in WEB_PORTS or
                        "http" in service.lower() or
                        "ssl" in service.lower()
                    )

                    if is_web:
                        scheme = "https" if (
                            "ssl" in service.lower() or
                            "https" in service.lower() or
                            port in {443, 8443, 9443}
                        ) else "http"

                        # Porta standard -> omettila dall'URL
                        if (scheme == "http" and port == 80) or \
                           (scheme == "https" and port == 443):
                            url = f"{scheme}://{clean_target}"
                        else:
                            url = f"{scheme}://{clean_target}:{port}"

                        web_urls.append({
                            "url": url,
                            "port": port,
                            "service": service,
                            "version": version_string
                        })
                    else:
                        if product:  # Solo se abbiamo info utili per CVE
                            non_web_services.append({
                                "port": port,
                                "service": service,
                                "version": version_string,
                                "cve_query": f"{product} {version}".strip()
                            })

            return ToolResult(
                success=True,
                data={
                    "original_target": target,
                    "resolved_ip": scanned_host,
                    "os_detection": os_info,
                    "open_ports": open_ports,
                    "web_endpoints": web_urls,        # <-- URL pronti per Nuclei
                    "non_web_services": non_web_services,  # <-- Query pronte per CVE
                    "summary": (
                        f"{len(open_ports)} porte aperte | "
                        f"{len(web_urls)} endpoint web | "
                        f"{len(non_web_services)} servizi non-web"
                    )
                }
            )

        except nmap.PortScannerError as e:
            return ToolResult(
                success=False,
                error_message=f"Errore Nmap (permessi mancanti o nmap non installato): {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Errore critico durante la scansione: {str(e)}"
            )