from agent.brain import ask

def research_quotes(topic):
    return ask(f'''Gunakan web search untuk mencari 5 quote terdokumentasi yang relevan dengan topik: {topic}. Jangan mengarang. Sertakan tokoh, quote asli, karya/peristiwa, dan sumber yang dapat ditelusuri.''')
