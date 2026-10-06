import os
from dotenv import load_dotenv
load_dotenv()
AGENT_MODEL = os.getenv('AGENT_MODEL','llama-3.3-70b-versatile')
MAX_QUOTE_ATTEMPTS = int(os.getenv('MAX_QUOTE_ATTEMPTS','3'))
MIN_CONTENT_SCORE = int(os.getenv('MIN_CONTENT_SCORE','75'))
