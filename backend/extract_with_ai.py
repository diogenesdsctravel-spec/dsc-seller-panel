"""
Módulo para extração inteligente de dados de viagem usando OpenAI.

Responsabilidades:
- Extrair dados estruturados de PDFs de orçamento
- Gerar roteiro inteligente via IA
- Buscar e associar imagens curadas para cada destino
- Fallback para dados simulados quando necessário

Depende de: supabase_images, generate_itinerary
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
import PyPDF2

# Single source of truth para imagens
from supabase_images import (
    get_images_for_all_cities,
    get_hero_image_for_trip,
    buscar_imagem,
)


# ============================================================================
# EXTRAÇÃO DE PDF
# ============================================================================

def read_pdf_text(pdf_path: Path) -> str:
    """
    Extrai texto de um arquivo PDF.

    Args:
        pdf_path: Caminho para o arquivo PDF

    Returns:
        Texto extraído do PDF
    """
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"⚠️ Erro ao ler PDF {pdf_path}: {e}")
        return ""


# ============================================================================
# EXTRAÇÃO DE DESTINOS
# ============================================================================

def extract_destinations_from_data(data: Dict) -> List[str]:
    """
    Extrai lista única de destinos dos hotéis.

    Args:
        data: Dados estruturados da viagem

    Returns:
        Lista de cidades únicas
    """
    destinations: List[str] = []

    if "hoteis" in data and isinstance(data["hoteis"], list):
        for hotel in data["hoteis"]:
            if "cidade" in hotel:
                city = hotel["cidade"].strip()
                if city and city not in destinations:
                    destinations.append(city)

    print(
        f"🗺️ Destinos identificados: "
        f"{', '.join(destinations) if destinations else 'Nenhum'}"
    )
    return destinations


# ============================================================================
# EXTRAÇÃO PRINCIPAL
# ============================================================================

def extract_travel_data(trip_folder: Path, cliente_nome: str = "") -> Dict:
    """
    Extrai dados de viagem dos arquivos usando OpenAI.

    Fluxo:
    1. Lê todos os PDFs da pasta
    2. Envia para OpenAI para extração estruturada
    3. Identifica destinos
    4. Busca imagens curadas no Supabase
    5. Gera roteiro inteligente
    6. Associa fotos específicas para cada dia

    Args:
        trip_folder: Pasta com os arquivos enviados
        cliente_nome: Nome do cliente (opcional)

    Returns:
        Dados estruturados completos da viagem
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada no arquivo .env")

    client = OpenAI(api_key=api_key)

    # Coletar conteúdo de todos os PDFs
    files_content: List[str] = []
    for file_path in trip_folder.glob("*"):
        if file_path.suffix.lower() == ".pdf":
            text = read_pdf_text(file_path)
            if text.strip():
                files_content.append(f"=== Arquivo: {file_path.name} ===\n{text}")

    # Fallback se não houver PDFs
    if not files_content:
        print("⚠️ Nenhum PDF encontrado, usando dados simulados")
        return get_mock_data(cliente_nome)

    all_text = "\n\n".join(files_content)

    # Prompt para extração estruturada
    prompt = f"""Analise o seguinte conteúdo de orçamento de viagem e extraia as informações em formato JSON.

CONTEÚDO DOS ARQUIVOS:
{all_text}

INSTRUÇÕES:
- Extraia TODAS as informações disponíveis
- Use o formato JSON exato especificado abaixo
- Se algum campo não estiver disponível, use valores razoáveis ou deixe vazio
- Datas no formato DD/MM ou DD/MM/AAAA
- Valores numéricos sem símbolos de moeda
- Para o campo "cliente", use: "{cliente_nome if cliente_nome else 'Cliente'}"

FORMATO JSON (retorne APENAS JSON, sem texto adicional):
{{
  "cliente": "{cliente_nome if cliente_nome else 'Cliente'}",
  "periodo": {{
    "inicio": "DD/MM",
    "fim": "DD/MM"
  }},
  "voos": [
    {{
      "origem": "Cidade (CÓDIGO)",
      "destino": "Cidade (CÓDIGO)",
      "data": "DD/MM",
      "horario_saida": "HH:MM",
      "horario_chegada": "HH:MM"
    }}
  ],
  "hoteis": [
    {{
      "cidade": "Cidade",
      "nome": "Nome do hotel",
      "noites": 3,
      "checkin": "DD/MM",
      "checkout": "DD/MM",
      "regime": "Tipo de alimentação"
    }}
  ],
  "passeios": [
    {{
      "nome": "Nome do passeio",
      "valor_por_pessoa": 100,
      "incluido": false
    }}
  ],
  "pacote_base": {{
    "descricao": "Aéreo + Hotel",
    "valor": 5000
  }}
}}"""

    try:
        # Chamar OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente especializado em extrair dados "
                        "de orçamentos de viagem. Retorne SEMPRE em formato "
                        "JSON válido."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        result_text = response.choices[0].message.content
        extracted_data = json.loads(result_text)

        # Garantir nome do cliente
        if cliente_nome:
            extracted_data["cliente"] = cliente_nome

        print(f"✅ Extração bem-sucedida de {len(files_content)} arquivo(s)")

        # Processar imagens
        destinations = extract_destinations_from_data(extracted_data)
        if destinations:
            print(f"🖼️ Buscando imagens para destinos: {destinations}")

            # Imagem hero
            hero_image = get_hero_image_for_trip(destinations)
            extracted_data["imagem_hero"] = hero_image

            # Imagens de todas as cidades
            all_images = get_images_for_all_cities(destinations)
            extracted_data["imagens_cidades"] = all_images

            print(f"✅ Imagens adicionadas para {len(destinations)} cidade(s)")
        else:
            print("⚠️ Nenhum destino identificado, imagem não adicionada")

        # Gerar roteiro
        from generate_itinerary import generate_itinerary

        print("📅 Gerando roteiro...")
        roteiro = generate_itinerary(extracted_data)
        extracted_data["roteiro"] = roteiro
        print(f"✅ Roteiro gerado: {len(roteiro)} dias")

        # Buscar fotos específicas para cada dia do roteiro
        if roteiro:
            print("📸 Buscando fotos específicas para cada dia do roteiro...")

            for dia in roteiro:
                landmark = dia.get("landmark")
                # Pegar cidade do primeiro hotel (simplificação)
                cidade = extracted_data.get("hoteis", [{}])[0].get("cidade", "")

                if landmark and cidade:
                    print(f"  Dia {dia.get('dia')}: {landmark}")

                    # Buscar foto curada com matching semântico
                    foto = buscar_imagem(cidade, landmark)

                    if foto:
                        dia["imagem_dia"] = foto
                        print("    💎 Foto curada encontrada")
                    else:
                        print("    ⚠️ Sem foto curada, usando fallback")
                        dia["imagem_dia"] = (
                            "https://images.unsplash.com/"
                            "photo-1488646953014-85cb44e25828?w=1200"
                        )

            print(f"✅ Fotos processadas para {len(roteiro)} dias")

        return extracted_data

    except Exception as e:
        print(f"❌ Erro na extração com IA: {e}")
        print("⚠️ Retornando dados simulados")
        return get_mock_data(cliente_nome)


# ============================================================================
# DADOS SIMULADOS (FALLBACK)
# ============================================================================

def get_mock_data(cliente_nome: str = "") -> Dict:
    """
    Retorna dados simulados caso a extração falhe.

    Args:
        cliente_nome: Nome do cliente

    Returns:
        Dados simulados completos
    """
    mock_data = {
        "cliente": cliente_nome if cliente_nome else "Cliente (dados simulados)",
        "periodo": {"inicio": "15/02", "fim": "22/02"},
        "voos": [
            {
                "origem": "São Paulo (GRU)",
                "destino": "Lima (LIM)",
                "data": "15/02",
                "horario_saida": "09:15",
                "horario_chegada": "14:30",
            }
        ],
        "hoteis": [
            {
                "cidade": "Lima",
                "nome": "Hotel (dados simulados)",
                "noites": 3,
                "checkin": "15/02",
                "checkout": "18/02",
                "regime": "Sem alimentação",
            }
        ],
        "passeios": [
            {
                "nome": "Passeio (dados simulados)",
                "valor_por_pessoa": 64,
                "incluido": False,
            }
        ],
        "pacote_base": {
            "descricao": "Aéreo + Hotel (casal)",
            "valor": 6656,
        },
    }

    # Adicionar imagem hero para dados simulados
    destinations = extract_destinations_from_data(mock_data)
    if destinations:
        mock_data["imagem_hero"] = get_hero_image_for_trip(destinations)

    return mock_data