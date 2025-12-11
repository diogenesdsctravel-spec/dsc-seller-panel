from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """
RETORNE APENAS JSON.
Exemplo:
[
  {"dia": 1, "titulo": "Chegada"}
]
"""

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=500
)

print("=== RAW RESPONSE ===")
print(response)

print("\n=== MESSAGE CONTENT ===")
print(response.choices[0].message.content)
print("TYPE:", type(response.choices[0].message.content))

