from agent import ask_agent
from tools import run_tool

def main() -> None:
    goal = """Buat satu konten Instagram berupa quote
yang relevan dengan kehidupan masyarakat Indonesia hari ini.""".strip()

    print("\n=== LANGKAH 1: AGENT MENENTUKAN TINDAKAN ===\n")
    decision = ask_agent(goal)
    print(decision)

    if decision == "TOOL: research_topic":
        print("\n=== LANGKAH 2: TOOL DIJALANKAN ===\n")
        research_result = run_tool("research_topic")
        print(research_result)

        print("\n=== LANGKAH 3: HASIL TOOL KEMBALI KE AGENT ===\n")
        print(ask_agent(goal, research_result))
    else:
        print("\nAgent belum meminta tool. Proses berhenti.\n")

if __name__ == "__main__":
    main()
