from agent.brain import ask

def create_plan(goal):
    return ask(f'''Kamu adalah AI Agent pembuat konten kutipan.
Tujuan: {goal}
Tentukan tindakan pertama. Jika perlu riset, jawab:
TOOL: research_topic
QUERY: <query>''')
