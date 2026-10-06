from agent.memory import load_memory, save_memory
from agent.planner import create_plan
from agent.state import AgentState
from config.settings import MAX_QUOTE_ATTEMPTS, MAX_REVISION_ATTEMPTS, MIN_CONTENT_SCORE
from tools.content import generate_content
from tools.evaluator import evaluate_content, parse_evaluation
from tools.image import generate_image_prompt
from tools.publisher import publish
from tools.quotes import research_quotes
from tools.research import research_topic
from tools.verification import verify_quote
from agent.brain import ask

def choose_topic(research: str, memory: dict) -> str:
    used = memory.get("used_topics", [])
    return ask(f"""Pilih SATU topik terbaik dari hasil riset berikut.
Hindari topik yang sudah dipakai: {used}
Jawab hanya nama topiknya.
RISET:
{research}""")

def choose_quote(candidates: str, memory: dict) -> tuple[str, str, str]:
    used = memory.get("used_quotes", [])
    result = ask(f"""Pilih SATU kandidat quote terbaik dari daftar berikut.
Hindari quote yang sudah dipakai: {used}
Jawab persis dalam format:
PERSON: ...
QUOTE: ...
SOURCE: ...
Jangan memilih parafrase.
KANDIDAT:
{candidates}""")
    person = quote = source = ""
    for line in result.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().upper()
            value = value.strip()
            if key == "PERSON": person = value
            elif key == "QUOTE": quote = value
            elif key == "SOURCE": source = value
    return person, quote, source

def run(goal: str) -> AgentState:
    state = AgentState(goal=goal)
    memory = load_memory()
    state.log("Membuat rencana kerja.")
    create_plan(goal)

    state.log("Riset topik.")
    research = research_topic(goal)
    state.topic = choose_topic(research, memory)
    state.log(f"Topik terpilih: {state.topic}")

    state.log("Mencari quote.")
    candidates = research_quotes(state.topic)
    state.quote_candidates = candidates

    verified = False
    for attempt in range(1, MAX_QUOTE_ATTEMPTS + 1):
        state.quote_attempts = attempt
        state.log(f"Memilih dan memverifikasi quote (percobaan {attempt}/{MAX_QUOTE_ATTEMPTS}).")
        state.person, state.quote, state.source = choose_quote(candidates, memory)
        if not state.person or not state.quote:
            candidates = research_quotes(state.topic)
            continue
        state.verification = verify_quote(state.person, state.quote, state.source)
        upper = state.verification.upper()
        if "STATUS: VERIFIED" in upper:
            verified = True
            break
        candidates = research_quotes(state.topic)

    if not verified:
        state.status = "STOPPED_QUOTE_NOT_VERIFIED"
        state.log("Berhenti: tidak menemukan quote yang cukup terverifikasi.")
        save_memory(memory)
        return state

    for attempt in range(0, MAX_REVISION_ATTEMPTS + 1):
        state.revision_attempts = attempt
        state.log(f"Membuat/evaluasi konten (iterasi {attempt + 1}).")
        feedback = ""
        if attempt:
            feedback = state.evaluation
        state.content = generate_content(
            state.topic, state.person, state.quote, state.verification, feedback
        )
        state.evaluation = evaluate_content(state.content)
        score, decision, _ = parse_evaluation(state.evaluation)
        state.log(f"Evaluasi: {score}/100 - {decision}")
        if decision == "PASS" and score >= MIN_CONTENT_SCORE:
            break
    else:
        state.status = "STOPPED_CONTENT_FAILED"
        state.log("Berhenti: konten tidak lolos evaluasi.")
        save_memory(memory)
        return state

    state.image_prompt = generate_image_prompt(state.content)
    result = publish(state.content)
    state.status = result.get("status", "UNKNOWN")

    memory.setdefault("used_quotes", []).append(state.quote)
    memory.setdefault("used_topics", []).append(state.topic)
    if result.get("status") == "PUBLISHED":
        memory.setdefault("published", []).append({
            "topic": state.topic,
            "person": state.person,
            "quote": state.quote,
        })
    save_memory(memory)
    state.log(f"Pipeline selesai dengan status: {state.status}.")
    return state
