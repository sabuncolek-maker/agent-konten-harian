from dataclasses import dataclass,field
@dataclass
class AgentState:
    goal:str; topic:str=""; context:str=""; person:str=""; quote:str=""; source:str=""; verification:str=""; content:str=""; evaluation:str=""; image_prompt:str=""; status:str="STARTING"; events:list[str]=field(default_factory=list)
    def log(self,message): self.events.append(message); print(f"[AGENT] {message}",flush=True)
