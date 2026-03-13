from tools.cve_tool import CveSearchTool
import json

def main():
    print("[*] Inizializzando il test del tool CVE...")
    cve_scanner = CveSearchTool()
    
    # Target: un software notoriamente vulnerabile
    software_target = "Apache 2.4.49" 
    
    print(f"[*] Cerco vulnerabilità note per: {software_target}")
    print("[*] Contattando il database NIST NVD (potrebbe volerci qualche secondo)...\n")
    
    # Eseguiamo la ricerca
    result = cve_scanner.execute(software_query=software_target)
    
    if result.success:
        print("[+] Ricerca completata con successo! Ecco i dati per l'IA:")
        print(json.dumps(result.data, indent=4))
    else:
        print(f"[-] Ricerca fallita. Errore riportato: {result.error_message}")

if __name__ == "__main__":
    main()