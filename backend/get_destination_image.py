"""
Módulo para buscar imagens de destinos turísticos via Unsplash API.

Responsável por:
- Buscar fotos profissionais de cidades/destinos
- Cache simples para evitar chamadas duplicadas
- Fallback para imagem genérica em caso de erro
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da API
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Imagem fallback (paisagem genérica de viagem)
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200"

# Cache em memória (simples, para evitar chamadas duplicadas na mesma sessão)
_image_cache = {}


def search_destination_image(city_name: str, country: Optional[str] = None) -> str:
    """
    Busca uma imagem profissional para um destino turístico.
    
    Args:
        city_name: Nome da cidade (ex: "Lima", "Cusco", "Paris")
        country: País opcional para maior precisão (ex: "Peru", "France")
    
    Returns:
        URL da imagem do Unsplash (alta resolução)
        
    Exemplos:
        >>> search_destination_image("Lima", "Peru")
        "https://images.unsplash.com/photo-..."
        
        >>> search_destination_image("Machu Picchu")
        "https://images.unsplash.com/photo-..."
    """
    
    # Verifica se API key está configurada
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️ UNSPLASH_ACCESS_KEY não configurado, usando imagem fallback")
        return FALLBACK_IMAGE
    
    # Monta query de busca
    search_query = f"{city_name} travel"
    if country:
        search_query = f"{city_name} {country} travel landmark"
    
    # Verifica cache
    cache_key = search_query.lower()
    if cache_key in _image_cache:
        print(f"✅ [CACHE HIT] Imagem de '{search_query}' já buscada")
        return _image_cache[cache_key]
    
    print(f"🔍 Buscando imagem para: {search_query}")
    
    try:
        # Faz requisição para Unsplash API
        response = requests.get(
            UNSPLASH_API_URL,
            params={
                "query": search_query,
                "per_page": 1,
                "orientation": "landscape",
                "content_filter": "high"
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"❌ Erro na API Unsplash: {response.status_code}")
            return FALLBACK_IMAGE
        
        data = response.json()
        
        if not data.get("results") or len(data["results"]) == 0:
            print(f"⚠️ Nenhuma imagem encontrada para '{search_query}'")
            return FALLBACK_IMAGE
        
        image_url = data["results"][0]["urls"]["regular"]
        _image_cache[cache_key] = image_url
        
        print(f"✅ Imagem encontrada: {image_url[:80]}...")
        return image_url
        
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout ao buscar imagem para '{search_query}'")
        return FALLBACK_IMAGE
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de rede ao buscar imagem: {str(e)}")
        return FALLBACK_IMAGE
        
    except Exception as e:
        print(f"❌ Erro inesperado ao buscar imagem: {str(e)}")
        return FALLBACK_IMAGE


def get_hero_image_for_trip(destinations: list[str]) -> str:
    """
    Busca a melhor imagem hero para uma viagem com múltiplos destinos.
    """
    
    if not destinations or len(destinations) == 0:
        print("⚠️ Nenhum destino fornecido")
        return FALLBACK_IMAGE
    
    iconic_keywords = [
        "machu picchu", "machu", "cusco",
        "paris", "eiffel", "coliseu", "rome",
        "tokyo", "dubai", "new york", "london"
    ]
    
    for destination in destinations:
        destination_lower = destination.lower()
        if any(keyword in destination_lower for keyword in iconic_keywords):
            print(f"🎯 Destino icônico detectado: {destination}")
            return search_destination_image(destination)
    
    print(f"📍 Usando primeiro destino: {destinations[0]}")
    return search_destination_image(destinations[0])


if __name__ == "__main__":
    print("🧪 Testando busca de imagens...\n")
    
    print("=" * 60)
    img1 = search_destination_image("Machu Picchu", "Peru")
    print(f"Resultado: {img1}\n")
    
    print("=" * 60)
    img2 = search_destination_image("Lima", "Peru")
    print(f"Resultado: {img2}\n")
    
    print("=" * 60)
    destinations = ["Lima", "Cusco", "Machu Picchu"]
    hero = get_hero_image_for_trip(destinations)
    print(f"Hero image: {hero}\n")
    
    print("✅ Testes concluídos!")
