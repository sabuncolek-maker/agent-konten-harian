from agent.brain import ask

def research_topic(query):
    return ask(f'''Gunakan web search untuk mencari 5 topik aktual dan relevan di Indonesia untuk: {query}. Prioritaskan sumber kredibel dan terbaru. Sertakan alasan dan sumber.''')
