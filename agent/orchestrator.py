import os
from agent.brain import ask
from agent.memory import load_memory, save_memory
from agent.planner import create_plan
from agent.state import AgentState
from tools.content import generate_content
from tools.evaluator import evaluate_content, parse_evaluation
from tools.image import generate_image_prompt
from tools.publisher import publish
from tools.quotes import research_quotes
from tools.research import research_topic
from tools.verification import verify_quote

MAX_QUOTE_ATTEMPTS = int(os.getenv("MAX_QUOTE_ATTEMPTS", "3"))
MAX_REVISION_ATTEMPTS = int(os.getenv("MAX_REVISION_ATTEMPTS", "2"))
MIN_CONTENT_SCORE = int(os.getenv("MIN_CONTENT_SCORE", "75"))

def choose_topic(research, memory):
    return ask(f"""Pilih SATU topik terbaik dari riset berikut.
Hindari topik yang sudah dipakai: {memory.get("used_topics", [])}
Jawab hanya nama topiknya.
RISET:
{research}""")

def choose_quote(candidates, memory):
    result = ask(f"""Pilih SATU kandidat quote terbaik.
Hindari quote yang sudah dipakai: {memory.get("used_quotes", [])}
Jawab persis:
PERSON: ...
QUOTE: ...
SOURCE: ...
Jangan memilih parafrase.
KANDIDAT:
{candidates}""")
    data = {"PERSON":"","QUOTE":"","SOURCE":""}
    for line in result.splitlines():
        if ":" in line:
            k,v = line.split(":",1)
            if k.strip().upper() in data:
                data[k.strip().upper()] = v.strip()
    return data["PERSON"], data["QUOTE"], data["SOURCE"]

def run(goal):
    state = AgentState(goal=goal)
    memory = load_memory()
    state.log("Membuat rencana.")
    create_plan(goal)

    state.log("Riset topik.")
    research = research_topic(goal)
    state.topic = choose_topic(research, memory)
    state.log(f"Topik terpilih: {state.topic}")

    candidates = research_quotes(state.topic)
    verified = False

    for attempt in range(1, MAX_QUOTE_ATTEMPTS + 1):
        state.quote_attempts = attempt
        state.log(f"Verifikasi quote {attempt}/{MAX_QUOTE_ATTEMPTS}.")
        state.person, state.quote, state.source = choose_quote(candidates, memory)
        if not state.person or not state.quote:
            candidates = research_quotes(state.topic)
            continue
        state.verification = verify_quote(state.person, state.quote, state.source)
        if "STATUS: VERIFIED" in state.verification.upper():
            verified = True
            break
        candidates = research_quotes(state.topic)

    if not verified:
        state.status = "STOPPED_QUOTE_NOT_VERIFIED"
        state.log("Berhenti: quote tidak cukup terverifikasi.")
        save_memory(memory)
        return state

    for attempt in range(MAX_REVISION_ATTEMPTS + 1):
        state.revision_attempts = attempt
        feedback = state.evaluation if attempt else ""
        state.log(f"Generate/evaluasi konten iterasi {attempt + 1}.")
        state.content = generate_content(state.topic, state.person, state.quote, state.verification, feedback)
        state.evaluation = evaluate_content(state.content)
        score, decision, _ = parse_evaluation(state.evaluation)
        state.log(f"Score {score}/100 - {decision}")
        if decision == "PASS" and score >= MIN_CONTENT_SCORE:
            break
    else:
        state.status = "STOPPED_CONTENT_FAILED"
        save_memory(memory)
        return state

    state.image_prompt = generate_image_prompt(state.content)
    result = publish(state.content)
    state.status = result.get("status", "UNKNOWN")

    memory.setdefault("used_quotes", []).append(state.quote)
    memory.setdefault("used_topics", []).append(state.topic)
    save_memory(memory)
    state.log(f"Pipeline selesai: {state.status}")
    return state
