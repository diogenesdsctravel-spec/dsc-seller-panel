"""
Gera roteiro dia-a-dia usando OpenAI GPT-4.
"""

import os
from openai import OpenAI
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()


def generate_itinerary(trip_data: dict) -> list[dict]:
    """
    Gera roteiro inteligente baseado nos dados da viagem.
    
    Args:
        trip_data: Dados extraídos da viagem (voos, hotéis, passeios, etc)
    
    Returns:
        Lista de dias do roteiro com título, descrição, transfer, dica, etc.
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY não configurada")
        return []
    
    client = OpenAI(api_key=api_key)
    
    # Extrair informações essenciais
    periodo = trip_data.get("periodo", {})
    voos = trip_data.get("voos", [])
    hoteis = trip_data.get("hoteis", [])
    passeios = trip_data.get("passeios", [])
    
    inicio = periodo.get("inicio", "")
    fim = periodo.get("fim", "")
    
    # Identificar se tem transfer nos passeios
    tem_transfer = any("transfer" in str(p.get("nome", "")).lower() for p in passeios)
    
    # Montar contexto para a IA
    prompt = f"""Crie um roteiro dia-a-dia COMPLETO para esta viagem a Buenos Aires:

PERÍODO: {inicio} a {fim}

VOOS:
{json.dumps(voos, indent=2, ensure_ascii=False)}

HOTÉIS:
{json.dumps(hoteis, indent=2, ensure_ascii=False)}

PASSEIOS INCLUÍDOS:
{json.dumps(passeios, indent=2, ensure_ascii=False)}

REGRAS OBRIGATÓRIAS:

1. DIA DE CHEGADA (Dia 1):
   - Título: "Chegada a Buenos Aires"
   - Horário: Mostrar horário de chegada do voo
   - Descrição: 2-3 parágrafos sobre chegada, transfer, check-in e primeira noite
   - Transfer: "{('incluido' if tem_transfer else 'a-incluir')}"
   - Dica: Uma dica prática sobre o bairro do hotel

2. DIAS INTERMEDIÁRIOS (Dia 2 até penúltimo):
   - Título: Nome de atividade/bairro (ex: "City Tour por Buenos Aires", "Explorando Palermo")
   - Descrição: 2-3 parágrafos com sugestões de manhã, tarde e noite
   - Mencionar pontos turísticos: Obelisco, Teatro Colón, Casa Rosada, Puerto Madero, La Boca, Recoleta
   - Se tem passeio incluído: mencionar "✓ [Nome do passeio] incluído"
   - Dica: Dica sobre restaurantes, horários, transporte

3. DIA DE PARTIDA (Último dia):
   - Título: "Retorno"
   - Horário: Mostrar horário do voo de volta
   - Descrição: Check-out, transfer ao aeroporto, despedida
   - Transfer: "{('incluido' if tem_transfer else 'a-incluir')}"
   - Dica: Dica sobre check-in antecipado ou última compra

FORMATO JSON (retorne APENAS JSON array limpo, sem ```json):
[
  {{
    "dia": 1,
    "data": "30/01",
    "titulo": "Chegada a Buenos Aires",
    "horario": "Chegada às 17:00",
    "descricao": "Ao desembarcar no Aeroporto Ezeiza, um parceiro da DSC Travel estará aguardando para levá-lo ao Hotel Waldorf com conforto e segurança.\\n\\nApós o check-in, aproveite para descansar e se aclimatar à cidade. Buenos Aires te espera com sua energia vibrante!\\n\\nPara o jantar, explore os restaurantes do bairro - a culinária portenha é imperdível.",
    "transfer": "{('incluido' if tem_transfer else 'a-incluir')}",
    "dica": "O bairro de Recoleta é perfeito para sua primeira caminhada. Seguro e charmoso!"
  }},
  {{
    "dia": 2,
    "data": "31/01",
    "titulo": "City Tour por Buenos Aires",
    "horario": null,
    "descricao": "Comece o dia...",
    "transfer": null,
    "dica": "Reserve ingressos..."
  }}
]"""

    try:
        print("🤖 Chamando OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em roteiros de viagem. Crie roteiros detalhados, práticos e inspiradores. Retorne APENAS JSON array limpo, sem markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        print("✅ Resposta recebida")
        print(f"📏 Tamanho: {len(result_text)} caracteres")
        
        # Limpar markdown se houver
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])
        
        # Parse
        dias = json.loads(result_text)
        
        if not isinstance(dias, list):
            print(f"❌ Não é lista, é {type(dias)}")
            return []
        
        print(f"✅ Roteiro gerado com {len(dias)} dias")
        return dias
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        print(f"Primeiros 300 chars: {result_text[:300]}")
        return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    test_data = {
        "periodo": {"inicio": "30/01", "fim": "06/02"},
        "voos": [
            {"origem": "VDC", "destino": "Buenos Aires (AEP)", "horario_chegada": "17:00", "data": "30/01"},
            {"origem": "Buenos Aires (EZE)", "destino": "VDC", "horario_saida": "02:30", "data": "06/02"}
        ],
        "hoteis": [
            {"cidade": "Buenos Aires", "nome": "Waldorf Hotel", "noites": 7, "checkin": "30/01", "checkout": "06/02"}
        ],
        "passeios": []
    }
    
    roteiro = generate_itinerary(test_data)
    print("\n📋 ROTEIRO GERADO:")
    print(json.dumps(roteiro, indent=2, ensure_ascii=False))
