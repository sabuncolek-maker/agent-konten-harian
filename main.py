from agent.brain import ask


def run():
    goal = 'Buat satu konten Instagram berupa quote yang relevan dengan kehidupan masyarakat Indonesia hari ini.'
    return ask(f'''Kamu adalah AI Agent. Tujuan: {goal}\nKamu memiliki tools: research_topic, research_quotes, verify_quote, generate_content, evaluate_content, generate_image_prompt, publish. Tentukan tindakan berikutnya dan alasannya.''')


if __name__ == '__main__':
    print(run())
