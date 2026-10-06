import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = os.getenv('AGENT_MODEL', 'llama-3.3-70b-versatile')

def ask(prompt: str) -> str:
    response = client.chat.completions.create(model=MODEL, messages=[{'role':'user','content':prompt}])
    return (response.choices[0].message.content or '').strip()
