from agent import ask_agent


def main() -> None:
    goal = """
Buat satu konten Instagram berupa quote
yang relevan dengan kehidupan masyarakat Indonesia hari ini.
""".strip()

    result = ask_agent(goal)

    print("\n=== HASIL AGENT ===\n")
    print(result)


if __name__ == "__main__":
    main()
