from agent.orchestrator import run
GOAL="Cari satu kutipan dari tokoh atau pendahulu yang relevan dengan kondisi masyarakat Indonesia saat ini, lalu jadikan konten Instagram."
if __name__=="__main__":
    state=run(GOAL)
    print("\n=== HASIL AGENT ===")
    print("STATUS:",state.status)
    print("KONDISI:",state.topic)
    print("TOKOH:",state.person)
    print("QUOTE:",state.quote)
    print("VERIFIKASI:\n",state.verification)
    print("KONTEN:\n",state.content)
    print("EVALUASI:\n",state.evaluation)
    print("IMAGE PROMPT:\n",state.image_prompt)
