from tools.nmap_tool import NmapScannerTool
import json

def main():
    print("[*] Inizializzando il test del tool Nmap...")
    scanner = NmapScannerTool()
    
    # Usiamo il server di test ufficiale fornito dagli sviluppatori di Nmap
    target_ip = "scanme.nmap.org" 
    
    print(f"[*] Eseguendo la scansione su: {target_ip}")
    print("[*] Attendere, potrebbe volerci qualche secondo (Fast Mode attiva)...\n")
    
    # Eseguiamo il metodo execute della nostra classe
    result = scanner.execute(target=target_ip)
    
    # Verifichiamo il risultato formattato
    if result.success:
        print("[+] Scansione completata con successo! Ecco i dati per l'IA:")
        # Stampiamo il dizionario formattato come JSON leggibile
        print(json.dumps(result.data, indent=4))
    else:
        print(f"[-] Scansione fallita. Errore riportato: {result.error_message}")

if __name__ == "__main__":
    main()