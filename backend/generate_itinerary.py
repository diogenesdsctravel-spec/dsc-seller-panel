"""
Gera roteiro dia-a-dia usando OpenAI GPT-4.
"""

import os
import json
import logging
from openai import OpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Importar configurações
from config import ITINERARY_CONFIG, LANDMARK_DB

load_dotenv()

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        logger.error("❌ OPENAI_API_KEY não configurada")
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
    cidade_principal = ITINERARY_CONFIG.DEFAULT_CITY
    if hoteis and len(hoteis) > 0:
        cidade_principal = hoteis[0].get("cidade", ITINERARY_CONFIG.DEFAULT_CITY)
    
    # Identificar se tem transfer nos passeios
    tem_transfer = any("transfer" in str(p.get("nome", "")).lower() for p in passeios)
    
    # Buscar landmarks da cidade
    landmarks_texto = LANDMARK_DB.get_landmarks_text(cidade_principal)
    
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
   - VARIE os bairros/locais a cada dia
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
{landmarks_texto}

FORMATO JSON (retorne APENAS JSON array limpo, sem ```json):
[
  {{
    "dia": 1,
    "data": "30/01",
    "titulo": "Chegada a {cidade_principal}",
    "landmark": "{cidade_principal} cityscape",
    "horario": "Chegada às 17:00",
    "descricao": "...",
    "transfer": "{('incluido' if tem_transfer else 'a-incluir')}",
    "dica": "..."
  }}
]

IMPORTANTE: CADA DIA DEVE TER UM LANDMARK DIFERENTE para garantir variedade visual nas fotos!"""

    try:
        logger.info(f"🤖 Gerando roteiro para {cidade_principal}...")
        
        response = client.chat.completions.create(
            model=ITINERARY_CONFIG.AI_MODEL,
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
            temperature=ITINERARY_CONFIG.AI_TEMPERATURE,
            max_tokens=ITINERARY_CONFIG.AI_MAX_TOKENS,
            timeout=ITINERARY_CONFIG.API_TIMEOUT
        )
        
        result_text = response.choices[0].message.content.strip()
        
        logger.info(f"✅ Resposta recebida ({len(result_text)} caracteres)")
        
        # Limpar markdown se houver
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])
        
        # Parse
        dias = json.loads(result_text)
        
        if not isinstance(dias, list):
            logger.error(f"❌ Resposta não é lista, é {type(dias)}")
            return []
        
        # Validar número de dias
        if len(dias) < ITINERARY_CONFIG.MIN_DAYS:
            logger.error(f"❌ Roteiro muito curto: {len(dias)} dias")
            return []
        
        if len(dias) > ITINERARY_CONFIG.MAX_DAYS:
            logger.warning(f"⚠️ Roteiro longo: {len(dias)} dias (máx recomendado: {ITINERARY_CONFIG.MAX_DAYS})")
        
        logger.info(f"✅ Roteiro gerado com {len(dias)} dias")
        
        # Validar que todos os dias têm landmark
        for dia in dias:
            if "landmark" not in dia:
                logger.warning(f"⚠️ Dia {dia.get('dia')} sem landmark, adicionando genérico")
                dia["landmark"] = f"{cidade_principal} cityscape"
        
        return dias
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON inválido: {e}")
        logger.debug(f"Primeiros 300 chars: {result_text[:300]}")
        return []
    except Exception as e:
        logger.error(f"❌ Erro ao gerar roteiro: {e}")
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
    
    logger.info("=" * 70)
    logger.info("🧪 TESTE DE GERAÇÃO DE ROTEIRO")
    logger.info("=" * 70)
    
    roteiro = generate_itinerary(test_data)
    
    if roteiro:
        logger.info(f"\n✅ Roteiro gerado com {len(roteiro)} dias")
        logger.info(f"Landmarks: {[d.get('landmark') for d in roteiro]}")
    else:
        logger.error("❌ Falha ao gerar roteiro")
