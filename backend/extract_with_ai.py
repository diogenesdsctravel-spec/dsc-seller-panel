import os
import json
from pathlib import Path
from openai import OpenAI
import PyPDF2


def read_pdf_text(pdf_path: Path) -> str:
    """Extrai texto de um arquivo PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Erro ao ler PDF {pdf_path}: {e}")
        return ""


def extract_destinations_from_data(data: dict) -> list[str]:
    """Extrai lista de destinos dos HOTÉIS apenas."""
    destinations = []
    
    # Extrair apenas de hotéis
    if "hoteis" in data and isinstance(data["hoteis"], list):
        for hotel in data["hoteis"]:
            if "cidade" in hotel:
                city = hotel["cidade"].strip()
                if city and city not in destinations:
                    destinations.append(city)
    
    print(f"🗺️ Destinos identificados: {', '.join(destinations) if destinations else 'Nenhum'}")
    return destinations


def extract_travel_data(trip_folder: Path, cliente_nome: str = "") -> dict:
    """
    Extrai dados de viagem dos arquivos usando OpenAI.
    
    Args:
        trip_folder: Pasta com os arquivos enviados
        cliente_nome: Nome do cliente (opcional)
        
    Returns:
        Dados estruturados da viagem (com imagem do destino e roteiro)
    """
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada no arquivo .env")
    
    client = OpenAI(api_key=api_key)
    
    # Ler todos os arquivos da pasta
    files_content = []
    for file_path in trip_folder.glob("*"):
        if file_path.suffix.lower() == '.pdf':
            text = read_pdf_text(file_path)
            if text.strip():
                files_content.append(f"=== Arquivo: {file_path.name} ===\n{text}")
    
    if not files_content:
        print("⚠️ Nenhum PDF encontrado, usando dados simulados")
        return get_mock_data(cliente_nome)
    
    all_text = "\n\n".join(files_content)
    
    # Criar prompt estruturado para extração
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
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em extrair dados de orçamentos de viagem. Retorne SEMPRE em formato JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        extracted_data = json.loads(result_text)
        
        # Garantir que o nome do cliente está correto
        if cliente_nome:
            extracted_data["cliente"] = cliente_nome
        
        print(f"✅ Extração bem-sucedida de {len(files_content)} arquivo(s)")
        
        # Buscar múltiplas imagens para cada cidade
        destinations = extract_destinations_from_data(extracted_data)
        if destinations:
            print(f"🖼️ Buscando imagens para destinos: {destinations}")
            
            from image_search import get_images_for_all_cities, get_hero_image_for_trip
            
            # Hero image (primeira foto da primeira cidade)
            hero_image = get_hero_image_for_trip(destinations)
            extracted_data["imagem_hero"] = hero_image
            
            # Múltiplas imagens para cada cidade
            all_images = get_images_for_all_cities(destinations)
            extracted_data["imagens_cidades"] = all_images
            
            print(f"✅ Imagens adicionadas para {len(destinations)} cidade(s)")
        else:
            print("⚠️ Nenhum destino identificado, imagem não adicionada")
        
        # 🆕 GERAR ROTEIRO COM IA
        from generate_itinerary import generate_itinerary
        
        print("📅 Gerando roteiro...")
        roteiro = generate_itinerary(extracted_data)
        extracted_data["roteiro"] = roteiro
        print(f"✅ Roteiro gerado: {len(roteiro)} dias")
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ Erro na extração com IA: {e}")
        print("⚠️ Retornando dados simulados")
        return get_mock_data(cliente_nome)


def get_mock_data(cliente_nome: str = "") -> dict:
    """Retorna dados simulados caso a extração falhe."""
    
    from image_search import get_hero_image_for_trip
    
    mock_data = {
        "cliente": cliente_nome if cliente_nome else "Cliente (dados simulados)",
        "periodo": {
            "inicio": "15/02",
            "fim": "22/02"
        },
        "voos": [
            {
                "origem": "São Paulo (GRU)",
                "destino": "Lima (LIM)",
                "data": "15/02",
                "horario_saida": "09:15",
                "horario_chegada": "14:30"
            }
        ],
        "hoteis": [
            {
                "cidade": "Lima",
                "nome": "Hotel (dados simulados)",
                "noites": 3,
                "checkin": "15/02",
                "checkout": "18/02",
                "regime": "Sem alimentação"
            }
        ],
        "passeios": [
            {
                "nome": "Passeio (dados simulados)",
                "valor_por_pessoa": 64,
                "incluido": False
            }
        ],
        "pacote_base": {
            "descricao": "Aéreo + Hotel (casal)",
            "valor": 6656
        }
    }
    
    # Adicionar imagem mesmo nos dados simulados
    destinations = extract_destinations_from_data(mock_data)
    if destinations:
        mock_data["imagem_hero"] = get_hero_image_for_trip(destinations)
    
    return mock_data