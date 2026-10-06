from agent import analyze_research, ask_agent
from tools import run_tool


def main() -> None:
    goal = """Buat satu konten Instagram berupa quote
yang relevan dengan kehidupan masyarakat Indonesia hari ini.""".strip()

    print("\n=== LANGKAH 1: AGENT MENENTUKAN TINDAKAN ===\n")
    decision = ask_agent(goal)
    print(decision)

    if not decision.startswith("TOOL: research_topic"):
        print("\nAgent tidak meminta research tool. Proses berhenti.\n")
        return

    query = decision.split("QUERY:", 1)[1].strip()

    print("\n=== LANGKAH 2: RESEARCH INTERNET ===\n")
    print(f"Query: {query}\n")

    research_result = run_tool("research_topic", query=query)
    print(research_result)

    print("\n=== LANGKAH 3: AGENT MENGANALISIS HASIL RISET ===\n")
    final_decision = analyze_research(goal, research_result)
    print(final_decision)


if __name__ == "__main__":
    main()
