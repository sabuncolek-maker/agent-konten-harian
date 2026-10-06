from dataclasses import dataclass, field

@dataclass
class AgentState:
    goal: str
    topic: str = ""
    quote_candidates: str = ""
    person: str = ""
    quote: str = ""
    source: str = ""
    verification: str = ""
    content: str = ""
    evaluation: str = ""
    image_prompt: str = ""
    status: str = "STARTING"
    quote_attempts: int = 0
    revision_attempts: int = 0
    events: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        self.events.append(message)
        print(f"[AGENT] {message}")
