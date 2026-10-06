import os

from agent.brain import ask, MODEL, RateLimitError
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

def extract_field(text: str, label: str) -> str:
    for line in text.splitlines():
        if line.strip().upper().startswith(label.upper() + ":"):
            return line.split(":", 1)[1].strip()
    return ""

def choose_quote(candidates, memory):
    return ask(f"""Pilih SATU kandidat quote terbaik dari hasil web search berikut.

Topik: {memory.get("_current_topic", "")}
Hindari quote yang sudah dipakai: {memory.get("used_quotes", [])}

Syarat:
- tokoh manusia nyata
- quote berupa kutipan langsung
- kandidat harus relevan dengan topik
- pilih bukti sumber paling kuat
- jangan memilih parafrase
- jangan membuat quote baru

Jawab persis:
PERSON: ...
QUOTE: ...
SOURCE: ...

HASIL WEB:
{candidates}""", model=MODEL, max_tokens=800)

def parse_quote(result: str):
    return (
        extract_field(result, "PERSON"),
        extract_field(result, "QUOTE"),
        extract_field(result, "SOURCE"),
    )

def run(goal):
    state = AgentState(goal=goal)
    memory = load_memory()

    try:
        state.log("Membuat rencana.")
        create_plan(goal)

        state.log("Riset topik dari web.")
        research = research_topic(goal, memory.get("used_topics", []))

        state.topic = extract_field(research, "TOPIK")
        if not state.topic:
            raise RuntimeError("Research model tidak mengembalikan TOPIK.")
        state.log(f"Topik terpilih: {state.topic}")

        memory["_current_topic"] = state.topic
        candidates = research_quotes(state.topic)

        verified = False
        for attempt in range(1, MAX_QUOTE_ATTEMPTS + 1):
            state.quote_attempts = attempt
            state.log(f"Verifikasi quote {attempt}/{MAX_QUOTE_ATTEMPTS}.")

            selection = choose_quote(candidates, memory)
            state.person, state.quote, state.source = parse_quote(selection)

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
            memory.pop("_current_topic", None)
            save_memory(memory)
            return state

        for attempt in range(MAX_REVISION_ATTEMPTS + 1):
            state.revision_attempts = attempt
            feedback = state.evaluation if attempt else ""
            state.log(f"Generate/evaluasi konten iterasi {attempt + 1}.")

            state.content = generate_content(
                state.topic,
                state.person,
                state.quote,
                state.verification,
                feedback,
            )
            state.evaluation = evaluate_content(state.content)
            score, decision, evaluation_text = parse_evaluation(state.evaluation)
            state.log(f"Score {score}/100 - {decision}")

            if decision == "PASS" and score >= MIN_CONTENT_SCORE:
                break
        else:
            state.status = "STOPPED_CONTENT_FAILED"
            memory.pop("_current_topic", None)
            save_memory(memory)
            return state

        state.image_prompt = generate_image_prompt(state.content)
        result = publish(state.content)
        state.status = result.get("status", "UNKNOWN")

        memory.setdefault("used_quotes", []).append(state.quote)
        memory.setdefault("used_topics", []).append(state.topic)
        memory.setdefault("published", []).append({
            "topic": state.topic,
            "quote": state.quote,
            "person": state.person,
            "status": state.status,
        })
        memory.pop("_current_topic", None)
        save_memory(memory)

        state.log(f"Pipeline selesai: {state.status}")
        return state

    except RateLimitError as exc:
        state.status = "RATE_LIMITED"
        state.log(str(exc))
        memory.pop("_current_topic", None)
        save_memory(memory)
        return state
    except Exception as exc:
        state.status = "ERROR"
        state.log(f"Error: {type(exc).__name__}: {exc}")
        memory.pop("_current_topic", None)
        save_memory(memory)
        return state
