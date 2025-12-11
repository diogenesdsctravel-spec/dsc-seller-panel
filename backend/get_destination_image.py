"""
Módulo para buscar imagens de destinos turísticos via Unsplash API.
"""

import os
import requests
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200"

_image_cache = {}


def search_multiple_images(city_name: str, count: int = 3) -> List[str]:
    """
    Busca MÚLTIPLAS fotos diferentes para uma cidade.
    
    Args:
        city_name: Nome da cidade
        count: Quantas fotos buscar (padrão: 3)
    
    Returns:
        Lista de URLs de imagens DIFERENTES
    """
    
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️ UNSPLASH_ACCESS_KEY não configurado")
        return [FALLBACK_IMAGE] * count
    
    search_query = f"{city_name} travel landmark colorful vibrant"
    
    cache_key = f"{search_query.lower()}_{count}"
    if cache_key in _image_cache:
        print(f"✅ [CACHE HIT] Imagens de '{city_name}' já buscadas")
        return _image_cache[cache_key]
    
    print(f"🔍 Buscando {count} imagens para: {city_name}")
    
    try:
        response = requests.get(
            UNSPLASH_API_URL,
            params={
                "query": search_query,
                "per_page": count + 5,
                "orientation": "landscape",
                "content_filter": "high",
            },
            headers={
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code}")
            return [FALLBACK_IMAGE] * count
        
        data = response.json()
        results = data.get("results", [])
        
        if len(results) == 0:
            print(f"⚠️ Nenhuma imagem encontrada para '{city_name}'")
            return [FALLBACK_IMAGE] * count
        
        # Filtrar fotos coloridas (remover P&B)
        colorful_results = []
        for result in results:
            color = result.get("color", "#000000")
            
            # Converter hex para RGB
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # Se RGB muito próximos = P&B, pular
            if abs(r - g) < 20 and abs(g - b) < 20 and abs(r - b) < 20:
                continue
            
            colorful_results.append(result)
            
            if len(colorful_results) >= count:
                break
        
        # Extrair URLs
        image_urls = [result["urls"]["regular"] for result in colorful_results]
        
        # Se não encontrou todas, preencher com fallback
        while len(image_urls) < count:
            image_urls.append(FALLBACK_IMAGE)
        
        _image_cache[cache_key] = image_urls
        
        print(f"✅ {len(image_urls)} imagens encontradas para {city_name}")
        return image_urls
        
    except Exception as e:
        print(f"❌ Erro ao buscar imagens: {str(e)}")
        return [FALLBACK_IMAGE] * count


def get_hero_image_for_trip(destinations: list[str]) -> str:
    """Busca a PRIMEIRA imagem (hero) do primeiro destino."""
    
    if not destinations or len(destinations) == 0:
        return FALLBACK_IMAGE
    
    print(f"📍 Buscando hero image para: {destinations[0]}")
    
    images = search_multiple_images(destinations[0], count=3)
    return images[0]


def get_images_for_all_cities(destinations: list[str]) -> dict:
    """
    Busca 3 fotos DIFERENTES para cada cidade.
    
    Returns:
        {
            "Buenos Aires": ["url1", "url2", "url3"],
            "Lima": ["url1", "url2", "url3"]
        }
    """
    
    result = {}
    
    for city in destinations:
        images = search_multiple_images(city, count=3)
        result[city] = images
    
    return result


if __name__ == "__main__":
    print("🧪 Testando busca de múltiplas imagens...\n")
    
    destinations = ["Buenos Aires", "Lima"]
    all_images = get_images_for_all_cities(destinations)
    
    for city, images in all_images.items():
        print(f"\n{city}:")
        for i, img in enumerate(images, 1):
            print(f"  Foto {i}: {img[:60]}...")
    
    print("\n✅ Testes concluídos!")
