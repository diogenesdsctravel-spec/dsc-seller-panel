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
        Lista de dias do roteiro com título, descrição, landmark (para busca de foto), etc.
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
    
    # Identificar cidade principal
    cidade_principal = "Buenos Aires"
    if hoteis and len(hoteis) > 0:
        cidade_principal = hoteis[0].get("cidade", "Buenos Aires")
    
    # Identificar se tem transfer nos passeios
    tem_transfer = any("transfer" in str(p.get("nome", "")).lower() for p in passeios)
    
    # Montar contexto para a IA
    prompt = f"""Crie um roteiro dia-a-dia COMPLETO para esta viagem a {cidade_principal}:

PERÍODO: {inicio} a {fim}

VOOS:
{json.dumps(voos, indent=2, ensure_ascii=False)}

HOTÉIS:
{json.dumps(hoteis, indent=2, ensure_ascii=False)}

PASSEIOS INCLUÍDOS:
{json.dumps(passeios, indent=2, ensure_ascii=False)}

REGRAS OBRIGATÓRIAS:

1. CAMPO "landmark" É OBRIGATÓRIO EM CADA DIA:
   - O campo "landmark" define qual FOTO será exibida naquele dia
   - Use APENAS o nome do lugar, sem cidade ou país
   - Exemplos corretos: "Obelisco", "Palermo", "La Boca", "Puerto Madero", "Recoleta"
   - Dia 1 (chegada): use "{cidade_principal} cityscape"
   - Último dia (partida): use "{cidade_principal} airport"

2. DIA DE CHEGADA (Dia 1):
   - Título: "Chegada a {cidade_principal}"
   - landmark: "{cidade_principal} cityscape"
   - Horário: Mostrar horário de chegada do voo
   - Descrição: 2-3 parágrafos sobre chegada, transfer, check-in e primeira noite
   - Transfer: "{('incluido' if tem_transfer else 'a-incluir')}"
   - Dica: Uma dica prática sobre o bairro do hotel

3. DIAS INTERMEDIÁRIOS (Dia 2 até penúltimo):
   - Título: Nome de atividade/bairro (ex: "City Tour", "Explorando Palermo", "La Boca e Caminito")
   - landmark: Nome DO LOCAL específico visitado (ex: "Obelisco", "Palermo", "La Boca", "Recoleta", "Puerto Madero")
   - Descrição: 2-3 parágrafos com sugestões de manhã, tarde e noite
   - VARIE os bairros/locais a cada dia: Obelisco, Teatro Colón, Palermo, La Boca, Recoleta, Puerto Madero
   - Se tem passeio incluído: mencionar "✓ [Nome do passeio] incluído"
   - Dica: Dica sobre restaurantes, horários, transporte

4. DIA DE PARTIDA (Último dia):
   - Título: "Retorno"
   - landmark: "{cidade_principal} airport"
   - Horário: Mostrar horário do voo de volta
   - Descrição: Check-out, transfer ao aeroporto, despedida
   - Transfer: "{('incluido' if tem_transfer else 'a-incluir')}"
   - Dica: Dica sobre check-in antecipado

LANDMARKS VÁLIDOS PARA {cidade_principal}:
- "Obelisco" (monumento icônico na Av. 9 de Julio)
- "Palermo" (bairro com parques e jardins)
- "La Boca" (bairro colorido com Caminito)
- "Puerto Madero" (bairro moderno à beira-mar)
- "Recoleta" (cemitério e arquitetura)
- "San Telmo" (feira de antiguidades)
- "Teatro Colón" (ópera house)
- "Casa Rosada" (Plaza de Mayo)

FORMATO JSON (retorne APENAS JSON array limpo, sem ```json):
[
  {{
    "dia": 1,
    "data": "30/01",
    "titulo": "Chegada a {cidade_principal}",
    "landmark": "{cidade_principal} cityscape",
    "horario": "Chegada às 17:00",
    "descricao": "Ao desembarcar no Aeroporto, um parceiro da DSC Travel estará aguardando para levá-lo ao hotel com conforto e segurança.\\n\\nApós o check-in, aproveite para descansar e se aclimatar à cidade. {cidade_principal} te espera com sua energia vibrante!\\n\\nPara o jantar, explore os restaurantes do bairro - a culinária local é imperdível.",
    "transfer": "{('incluido' if tem_transfer else 'a-incluir')}",
    "dica": "O bairro é perfeito para sua primeira caminhada. Seguro e charmoso!"
  }},
  {{
    "dia": 2,
    "data": "31/01",
    "titulo": "City Tour",
    "landmark": "Obelisco",
    "horario": null,
    "descricao": "Comece o dia explorando o coração da cidade. Visite o Obelisco, símbolo icônico de Buenos Aires, e caminhe pela Avenida 9 de Julio.\\n\\nÀ tarde, faça uma visita guiada ao majestoso Teatro Colón. À noite, aproveite para jantar em Puerto Madero.\\n\\nBuenos Aires é linda tanto de dia quanto à noite!",
    "transfer": null,
    "dica": "Reserve ingressos para o Teatro Colón com antecedência para garantir sua visita."
  }},
  {{
    "dia": 3,
    "data": "01/02",
    "titulo": "Explorando Palermo",
    "landmark": "Palermo",
    "horario": null,
    "descricao": "Passe a manhã caminhando pelo bairro de Palermo, conhecido por seus parques e jardins. Visite o Jardim Botânico e o Rosedal.\\n\\nÀ tarde, explore as boutiques e cafés charmosos de Palermo Soho. À noite, experimente a vibrante vida noturna de Palermo Hollywood.\\n\\nPalermo é perfeito para quem ama design, gastronomia e cultura.",
    "transfer": null,
    "dica": "Use o transporte público para se locomover - é eficiente e econômico."
  }}
]

IMPORTANTE: CADA DIA DEVE TER UM LANDMARK DIFERENTE para garantir variedade visual nas fotos!"""

    try:
        print("🤖 Chamando OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em roteiros de viagem. Crie roteiros detalhados, práticos e inspiradores. SEMPRE inclua o campo 'landmark' em cada dia. Retorne APENAS JSON array limpo, sem markdown."
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
        
        # Validar que todos os dias têm landmark
        for dia in dias:
            if "landmark" not in dia:
                print(f"⚠️ Dia {dia.get('dia')} sem landmark, adicionando genérico")
                dia["landmark"] = f"{cidade_principal} cityscape"
        
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