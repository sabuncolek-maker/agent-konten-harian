from agent.orchestrator import run

GOAL = "Buat satu konten Instagram berupa quote yang relevan dengan kehidupan masyarakat Indonesia hari ini."

if __name__ == "__main__":
    state = run(GOAL)
    print("\n=== HASIL AGENT ===")
    print("STATUS:", state.status)
    print("TOPIK:", state.topic)
    print("TOKOH:", state.person)
    print("QUOTE:", state.quote)
    print("VERIFIKASI:\n", state.verification)
    print("KONTEN:\n", state.content)
    print("EVALUASI:\n", state.evaluation)
    print("IMAGE PROMPT:\n", state.image_prompt)
