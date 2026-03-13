from agents.redteam_agent import RedTeamAgent

def main():
    print("[*] Inizializzando l'Agente RedTeam...")
    agent = RedTeamAgent()
    agent.test_connection()

if __name__ == "__main__":
    main()