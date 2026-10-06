import os
from dotenv import load_dotenv
load_dotenv()
AGENT_MODEL=os.getenv("AGENT_MODEL","deepseek-v4-pro")
FAST_MODEL=os.getenv("FAST_MODEL","deepseek-v4.1-flash")
VERIFICATION_MODEL=os.getenv("VERIFICATION_MODEL","deepseek-v4-pro")
MAX_REVISION_ATTEMPTS=int(os.getenv("MAX_REVISION_ATTEMPTS","2"))
MIN_CONTENT_SCORE=int(os.getenv("MIN_CONTENT_SCORE","75"))
