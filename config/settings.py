import os
from dotenv import load_dotenv

load_dotenv()

AGENT_MODEL = os.getenv("AGENT_MODEL", "openai/gpt-oss-120b")
RESEARCH_MODEL = os.getenv("RESEARCH_MODEL", "openai/gpt-oss-120b")
MAX_QUOTE_ATTEMPTS = int(os.getenv("MAX_QUOTE_ATTEMPTS", "3"))
MAX_REVISION_ATTEMPTS = int(os.getenv("MAX_REVISION_ATTEMPTS", "2"))
MIN_CONTENT_SCORE = int(os.getenv("MIN_CONTENT_SCORE", "75"))
