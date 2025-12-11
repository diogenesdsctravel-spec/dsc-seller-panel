"""
__probe_llm_itinerary_001.py
PROBE ISOLADO PARA TESTAR OpenAI + JSON
"""

import os
import json
from openai import OpenAI

print("✅ __probe_llm_itinerary_001.py CARREGADO")


def run_probe():
    print("🚀 FUNÇÃO run_probe EXECUTANDO")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY NÃO ENCONTRADA")

    client = OpenAI(api_key=api_key)

    prompt = """
RETORNE APENAS UM JSON ARRAY.
SEM TEXTO EXTRA.

Exemplo:
[
  {"dia": 1, "titulo": "Chegada"},
  {"dia": 2, "titulo": "Passeio"}
]
"""

    print("🤖 Chamando OpenAI...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500
    )

    print("✅ Resposta recebida")

    content = response.choices[0].message.content

    print("📥 RAW OUTPUT:")
    print(content)
    print("📌 TIPO:", type(content))

    clean = content.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        if len(parts) >= 2:
            clean = parts[1].strip()
            if clean.lower().startswith("json"):
                clean = clean[4:].lstrip()
    else:
        clean = content

    print("🧼 TEXTO APOS LIMPEZA:")
    print(clean)

    data = json.loads(clean)

    print("✅ JSON carregado com sucesso")
    print("📦 RESULTADO FINAL:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("🧪 EXECUÇÃO DIRETA DO PROBE")
    run_probe()

