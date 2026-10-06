from typing import Callable, Dict


def research_topic() -> str:
    """
    Tool pertama agent.
    Untuk sementara menggunakan data contoh agar mekanisme
    tool-calling dapat diuji tanpa API research eksternal.
    """
    return """
1. Fenomena orang Indonesia semakin lelah dengan tuntutan produktivitas.
2. Tekanan finansial dan biaya hidup menjadi topik yang banyak dibicarakan.
3. Banyak orang membandingkan hidupnya dengan orang lain melalui media sosial.
4. Tren mencari keseimbangan hidup semakin relevan di kalangan pekerja muda.
5. Kegagalan dan proses belajar kembali sering dibahas sebagai bagian dari kesuksesan.
""".strip()


TOOLS: Dict[str, Callable[[], str]] = {
    "research_topic": research_topic,
}


def run_tool(tool_name: str) -> str:
    if tool_name not in TOOLS:
        raise ValueError(f"Tool tidak ditemukan: {tool_name}")

    return TOOLS[tool_name]()
