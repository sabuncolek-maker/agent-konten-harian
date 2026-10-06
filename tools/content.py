from agent.brain import ask

def generate_content(topic, person, quote, verification):
    return ask(f'''Buat draft konten Instagram berdasarkan topik {topic}, tokoh {person}, quote {quote}, dan verifikasi {verification}. Buat hook, quote, atribusi, konteks, dan caption. Jangan mengubah quote asli.''')
