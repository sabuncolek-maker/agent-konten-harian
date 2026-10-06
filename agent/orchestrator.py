import json
import os

from agent.brain import RateLimitError
from agent.memory import load_memory, save_memory
from agent.planner import create_plan
from agent.state import AgentState
from tools.content import generate_content
from tools.evaluator import evaluate_content, parse_evaluation
from tools.image import generate_image_prompt
from tools.publisher import publish
from tools.quotes import research_quotes, select_quote
from tools.research import research_topic
from tools.verification import verify_quote

MAX_QUOTE_ATTEMPTS = int(os.getenv("MAX_QUOTE_ATTEMPTS", "6"))
MAX_REVISION_ATTEMPTS = int(os.getenv("MAX_REVISION_ATTEMPTS", "2"))
MIN_CONTENT_SCORE = int(os.getenv("MIN_CONTENT_SCORE", "75"))


def _json(text: str, default=None):
    try:
        return json.loads(text)
    except Exception:
        return default


def _verification_status(text: str) -> str:
    data = _json(text, {})
    status = str(data.get("status", "UNCERTAIN")).upper()
    return status if status in {"VERIFIED", "UNCERTAIN", "REJECTED"} else "UNCERTAIN"


def run(goal: str):
    state = AgentState(goal=goal)
    memory = load_memory()

    try:
        state.plan = create_plan(goal)
        state.log("Riset topik dari web.")
        state.research = research_topic(goal, memory.get("used_topics", []))

        research_data = _json(state.research)
        if not research_data or not research_data.get("topic"):
            raise RuntimeError("Research topik tidak menghasilkan JSON/topic yang valid.")

        state.topic = str(research_data["topic"]).strip()
        state.context = json.dumps(research_data, ensure_ascii=False)
        state.log(f"Topik terpilih: {state.topic}")

        state.log("Mencari kandidat quote secara semantik.")
        state.quote_candidates = research_quotes(state.context, memory.get("used_quotes", []))

        remaining = list(state.quote_candidates)
        rejected = []
        verified = False

        for attempt in range(1, MAX_QUOTE_ATTEMPTS + 1):
            state.quote_attempts = attempt
            if not remaining:
                state.log("Tidak ada kandidat quote tersisa.")
                break

            state.log(f"Seleksi + verifikasi quote {attempt}/{MAX_QUOTE_ATTEMPTS}.")
            candidate = select_quote(remaining, state.context, rejected)

            if not candidate:
                # Jangan mengulang kandidat yang sama jika selector gagal.
                remaining.pop(0)
                state.log("Selector gagal menghasilkan kandidat valid; kandidat dilewati.")
                continue

            state.person = candidate["person"]
            state.quote = candidate["quote"]
            state.source = candidate.get("source_url") or candidate.get("url", "")
            state.log(f"Kandidat: {state.person} — {state.quote}")

            state.verification = verify_quote(state.person, state.quote, state.source)
            status = _verification_status(state.verification)

            if status == "VERIFIED":
                verified = True
                state.log("Quote VERIFIED.")
                break

            rejected.append(state.quote)
            state.log(f"Quote {status}; kandidat dikeluarkan dari pool.")
            remaining = [
                item for item in remaining
                if item.get("url") != candidate.get("url")
                and item.get("snippet", "").strip() != candidate.get("snippet", "").strip()
            ]

        if not verified:
            state.status = "STOPPED_QUOTE_NOT_VERIFIED"
            state.log("Berhenti dengan aman: tidak ada quote yang cukup terverifikasi.")
            save_memory(memory)
            return state

        last_revision = ""
        passed = False
        for attempt in range(MAX_REVISION_ATTEMPTS + 1):
            state.revision_attempts = attempt
            state.log(f"Generate/evaluasi konten {attempt + 1}/{MAX_REVISION_ATTEMPTS + 1}.")
            state.content = generate_content(
                state.topic,
                state.person,
                state.quote,
                state.verification,
                last_revision,
            )
            state.evaluation = evaluate_content(state.content)
            score, decision, evaluation_text = parse_evaluation(state.evaluation)
            state.log(f"Score {score}/100 - {decision}")

            if decision == "PASS" and score >= MIN_CONTENT_SCORE:
                passed = True
                break

            last_revision = evaluation_text

        if not passed:
            state.status = "STOPPED_CONTENT_FAILED"
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
            "source": state.source,
        })
        save_memory(memory)

        state.log(f"Pipeline selesai: {state.status}")
        return state

    except RateLimitError as exc:
        state.status = "RATE_LIMITED"
        state.log(str(exc))
        save_memory(memory)
        return state
    except Exception as exc:
        state.status = "ERROR"
        state.log(f"Error: {type(exc).__name__}: {exc}")
        save_memory(memory)
        return state
