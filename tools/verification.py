from agent.brain import ask

def verify_quote(person, quote, source_hint=''):
    return ask(f'''Fact-check quote berikut menggunakan web search dan cari sumber primer bila memungkinkan.
Tokoh: {person}
Quote: {quote}
Sumber awal: {source_hint}
Tentukan STATUS: VERIFIED / UNCERTAIN / REJECTED. Sertakan bukti dan sumber.''')
