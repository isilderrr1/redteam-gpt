from tools.dirbuster_tool import WebDirBusterTool
import json

def main():
    print("[*] Inizializzando il test del tool DirBuster...")
    dirbuster = WebDirBusterTool()
    
    # Usiamo un sito web creato appositamente per essere scansionato legalmente
    target = "http://testphp.vulnweb.com" 
    
    print(f"[*] Cerco percorsi nascosti su: {target}")
    print("[*] Esecuzione in corso...\n")
    
    result = dirbuster.execute(target_url=target)
    
    if result.success:
        print("[+] Ricerca completata! Ecco i dati per l'IA:")
        print(json.dumps(result.data, indent=4))
    else:
        print(f"[-] Ricerca fallita: {result.error_message}")

if __name__ == "__main__":
    main()