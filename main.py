from agent import (
    analyze_research,
    ask_agent,
    decide_after_verification,
    select_quote,
)
from tools import run_tool


def main() -> None:
    goal = """Buat satu konten Instagram berupa quote
yang relevan dengan kehidupan masyarakat Indonesia hari ini.""".strip()

    print("\n=== 1. AGENT MEMINTA RISET TOPIK ===\n")
    decision = ask_agent(goal)
    print(decision)

    if not decision.startswith("TOOL: research_topic"):
        print("Agent tidak meminta research topic. Proses berhenti.")
        return

    query = decision.split("QUERY:", 1)[1].strip()

    print("\n=== 2. RESEARCH TOPIK ===\n")
    research_result = run_tool("research_topic", query=query)
    print(research_result)

    print("\n=== 3. AGENT MEMILIH TOPIK ===\n")
    topic_decision = analyze_research(goal, research_result)
    print(topic_decision)

    print("\n=== 4. RESEARCH QUOTE ===\n")
    quote_research = run_tool("research_quotes", topic=topic_decision)
    print(quote_research)

    print("\n=== 5. AGENT MEMILIH KANDIDAT QUOTE ===\n")
    selected = select_quote(topic_decision, quote_research)
    print(selected)

    person = ""
    quote = ""
    source_hint = ""

    for line in selected.splitlines():
        if line.startswith("PERSON:"):
            person = line.split(":", 1)[1].strip()
        elif line.startswith("QUOTE:"):
            quote = line.split(":", 1)[1].strip()
        elif line.startswith("SOURCE_HINT:"):
            source_hint = line.split(":", 1)[1].strip()

    if not person or not quote:
        print("\nFormat kandidat quote tidak valid. Proses berhenti.")
        return

    print("\n=== 6. VERIFIKASI QUOTE ===\n")
    verification = run_tool(
        "verify_quote",
        person=person,
        quote=quote,
        source_hint=source_hint,
    )
    print(verification)

    print("\n=== 7. AGENT MEMUTUSKAN HASIL VERIFIKASI ===\n")
    decision = decide_after_verification(
        topic=topic_decision,
        quote=quote,
        person=person,
        verification=verification,
    )
    print(decision)


if __name__ == "__main__":
    main()
