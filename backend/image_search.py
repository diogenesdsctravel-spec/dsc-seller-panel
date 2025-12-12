"""
Módulo para buscar imagens de destinos turísticos.

Estratégia híbrida:
1) Catálogo local (city_images.json)
2) Provedores externos: Unsplash, Pexels e Pixabay
3) Seleção das melhores imagens por landmarks e score simples
"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests

# Chaves de API (opcionais: se faltar alguma, apenas ignora o provedor)
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
PEXELS_API_URL = "https://api.pexels.com/v1/search"
PIXABAY_API_URL = "https://pixabay.com/api/"

FALLBACK_IMAGE = (
    "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200"
)

BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "city_images.json"

# Cache em memória
_image_cache: Dict[str, List[str]] = {}
_city_catalog: Dict[str, List[str]] = {}

# Landmarks icônicos por cidade
LANDMARKS: Dict[str, List[str]] = {
    "Buenos Aires": [
        "Obelisco Buenos Aires",
        "Puerto Madero Buenos Aires",
        "Casa Rosada Plaza Mayo",
    ],
    "Lima": ["Miraflores Lima Peru", "Plaza Mayor Lima", "Barranco Lima"],
    "Cusco": ["Machu Picchu Peru", "Plaza de Armas Cusco", "Sacsayhuaman Cusco"],
    "Machu Picchu": ["Machu Picchu sunrise", "Machu Picchu terraces", "Machu Picchu Huayna"],
    "São Paulo": ["Avenida Paulista São Paulo", "MASP São Paulo", "Parque Ibirapuera"],
    "Rio de Janeiro": ["Christ Redeemer Rio", "Copacabana Beach Rio", "Sugarloaf Mountain Rio"],
    "Salvador": ["Pelourinho Salvador", "Elevador Lacerda", "Farol da Barra Salvador"],
    "Vitória da Conquista": ["Vitória da Conquista Brazil", "Conquista Bahia cityscape"],
    "Paris": ["Eiffel Tower Paris", "Arc de Triomphe Paris", "Louvre Museum Paris"],
    "Roma": ["Colosseum Rome", "Trevi Fountain Rome", "Vatican Rome"],
    "Londres": ["Big Ben London", "Tower Bridge London", "London Eye"],
    "Lisboa": ["Lisbon tram 28", "Belem Tower Lisbon", "Alfama Lisbon"],
    "Madrid": ["Plaza Mayor Madrid", "Royal Palace Madrid", "Retiro Park Madrid"],
    "Barcelona": ["Sagrada Familia Barcelona", "Park Guell Barcelona", "La Rambla Barcelona"],
    "Nova York": ["Statue of Liberty", "Times Square New York", "Brooklyn Bridge"],
    "Orlando": ["Disney Castle Orlando", "Universal Studios Orlando", "Orlando theme park"],
    "Santiago": ["Santiago Chile skyline", "Cerro San Cristobal", "Plaza de Armas Santiago"],
    "Montevidéu": ["Montevideo Uruguay Rambla", "Ciudad Vieja Montevideo", "Palacio Salvo"],
    "San Pedro de Atacama": ["Valle de la Luna Atacama", "Atacama Desert", "Laguna Cejar"],
}


def load_city_catalog() -> Dict[str, List[str]]:
    """
    Carrega catálogo de imagens curadas do arquivo city_images.json.
    Formato esperado:
    {
        "Buenos Aires": ["url1", "url2"],
        "Lima": ["url1", "url2"]
    }
    """
    global _city_catalog

    if _city_catalog:
        return _city_catalog

    if not CATALOG_PATH.exists():
        print("ℹ️ city_images.json não encontrado, usando apenas provedores externos")
        _city_catalog = {}
        return _city_catalog

    try:
        with CATALOG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            normalized: Dict[str, List[str]] = {}
            for key, value in data.items():
                if not isinstance(value, list):
                    continue
                urls = [str(u) for u in value if isinstance(u, str) and u.strip()]
                if urls:
                    normalized[key.strip()] = urls
            _city_catalog = normalized
        else:
            _city_catalog = {}

        print(f"✅ Catálogo local carregado: {len(_city_catalog)} cidades")

    except Exception as e:
        print(f"⚠️ Erro ao carregar city_images.json: {e}")
        _city_catalog = {}

    return _city_catalog


def get_catalog_images(city_name: str, count: int = 3) -> List[str]:
    """Busca imagens do catálogo local (city_images.json)."""
    catalog = load_city_catalog()

    if not city_name:
        return []

    imgs = catalog.get(city_name)

    if not imgs:
        for key, value in catalog.items():
            if key.lower() == city_name.lower():
                imgs = value
                break

    if not imgs:
        return []

    if len(imgs) >= count:
        return imgs[:count]

    repeated = (imgs * (count // len(imgs) + 1))[:count]
    return repeated


# ---------- Provedores externos ----------


def _is_colorful(hex_color: str) -> bool:
    """Tenta identificar se a cor é colorida (evita P&B)."""
    if not hex_color or not hex_color.startswith("#") or len(hex_color) != 7:
        return True
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return not (abs(r - g) < 20 and abs(g - b) < 20)
    except Exception:
        return True


def search_unsplash(query: str, per_page: int = 10) -> List[Dict[str, Any]]:
    if not UNSPLASH_ACCESS_KEY:
        return []

    try:
        resp = requests.get(
            UNSPLASH_API_URL,
            params={
                "query": query,
                "per_page": per_page,
                "orientation": "landscape",
                "content_filter": "high",
                "order_by": "relevant",
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            timeout=6,
        )
        if resp.status_code != 200:
            print(f"⚠️ Unsplash erro {resp.status_code} para '{query}'")
            return []
        results = resp.json().get("results", [])
        photos = []
        for r in results:
            color = r.get("color") or "#000000"
            if not _is_colorful(color):
                continue
            photos.append(
                {
                    "provider": "unsplash",
                    "url": r["urls"]["regular"],
                    "thumb": r["urls"].get("small"),
                    "description": r.get("description") or r.get("alt_description") or "",
                    "likes": r.get("likes", 0),
                    "views": r.get("views") or 0,
                }
            )
        return photos
    except Exception as e:
        print(f"⚠️ Erro Unsplash '{query}': {e}")
        return []


def search_pexels(query: str, per_page: int = 10) -> List[Dict[str, Any]]:
    if not PEXELS_API_KEY:
        return []

    try:
        resp = requests.get(
            PEXELS_API_URL,
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=6,
        )
        if resp.status_code != 200:
            print(f"⚠️ Pexels erro {resp.status_code} para '{query}'")
            return []
        results = resp.json().get("photos", [])
        photos = []
        for p in results:
            photos.append(
                {
                    "provider": "pexels",
                    "url": p["src"]["large"],
                    "thumb": p["src"].get("medium"),
                    "description": p.get("alt") or "",
                    "likes": 0,
                    "views": 0,
                    "author": p.get("photographer"),
                }
            )
        return photos
    except Exception as e:
        print(f"⚠️ Erro Pexels '{query}': {e}")
        return []


def search_pixabay(query: str, per_page: int = 10) -> List[Dict[str, Any]]:
    if not PIXABAY_API_KEY:
        return []

    try:
        resp = requests.get(
            PIXABAY_API_URL,
            params={
                "key": PIXABAY_API_KEY,
                "q": query,
                "image_type": "photo",
                "orientation": "horizontal",
                "per_page": per_page,
                "safesearch": "true",
            },
            timeout=6,
        )
        if resp.status_code != 200:
            print(f"⚠️ Pixabay erro {resp.status_code} para '{query}'")
            return []
        hits = resp.json().get("hits", [])
        photos = []
        for h in hits:
            photos.append(
                {
                    "provider": "pixabay",
                    "url": h["largeImageURL"],
                    "thumb": h.get("previewURL"),
                    "description": h.get("tags", ""),
                    "likes": h.get("likes", 0),
                    "views": h.get("views", 0),
                }
            )
        return photos
    except Exception as e:
        print(f"⚠️ Erro Pixabay '{query}': {e}")
        return []


def _score_photo(photo: Dict[str, Any]) -> float:
    base = 0.0

    likes = int(photo.get("likes") or 0)
    views = int(photo.get("views") or 0)

    base += likes * 1.0
    base += views * 0.002

    provider = photo.get("provider")
    if provider == "unsplash":
        base += 5.0
    elif provider == "pexels":
        base += 4.0
    elif provider == "pixabay":
        base += 3.0

    return base


def search_multiple_images(city_name: str, count: int = 3) -> List[str]:
    """
    Busca fotos icônicas via múltiplas fontes (Unsplash, Pexels, Pixabay).
    Retorna apenas URLs das melhores imagens.
    """
    if not city_name:
        return [FALLBACK_IMAGE] * count

    cache_key = f"{city_name.lower()}_multi_{count}"
    if cache_key in _image_cache:
        print(f"💾 [CACHE] Imagens de '{city_name}'")
        return _image_cache[cache_key]

    queries = LANDMARKS.get(
        city_name, [f"{city_name} skyline travel city landmark"]
    )

    print("======================================================================")
    print(f"🔍 Buscando imagens externas para: {city_name}")
    print("======================================================================")

    candidates: List[Tuple[float, Dict[str, Any]]] = []

    for q in queries:
        unsplash_photos = search_unsplash(q, per_page=5)
        pexels_photos = search_pexels(q, per_page=5)
        pixabay_photos = search_pixabay(q, per_page=5)

        print(f"\nQuery: {q}")
        print(f"  Unsplash: {len(unsplash_photos)} fotos")
        print(f"  Pexels:   {len(pexels_photos)} fotos")
        print(f"  Pixabay:  {len(pixabay_photos)} fotos")

        for ph in unsplash_photos + pexels_photos + pixabay_photos:
            score = _score_photo(ph)
            candidates.append((score, ph))

    if not candidates:
        print("⚠️ Nenhuma imagem encontrada em provedores externos")
        imgs = [FALLBACK_IMAGE] * count
        _image_cache[cache_key] = imgs
        return imgs

    candidates.sort(key=lambda x: x[0], reverse=True)

    print("\nMelhores fotos (multifonte)")
    print("======================================================================")
    for i, (score, ph) in enumerate(candidates[: min(5, len(candidates))], start=1):
        print(f"[{i}] Fonte: {ph.get('provider')}  Score: {score:.1f}")
        print(f"    Desc: {ph.get('description', '')[:60]}")
        print(f"    URL:  {ph.get('url')}\n")

    urls: List[str] = []
    seen: set[str] = set()
    for score, ph in candidates:
        url = ph.get("url")
        if not url or url in seen:
            continue
        urls.append(url)
        seen.add(url)
        if len(urls) >= count:
            break

    while len(urls) < count:
        urls.append(FALLBACK_IMAGE)

    _image_cache[cache_key] = urls
    return urls


# ---------- Funções usadas pelo restante do sistema ----------


def get_hero_image_for_trip(destinations: List[str]) -> str:
    """Retorna uma imagem hero para a viagem."""
    if not destinations:
        return FALLBACK_IMAGE

    first_city = destinations[0]

    catalog_imgs = get_catalog_images(first_city, count=1)
    if catalog_imgs:
        print(f"📸 Hero de catálogo: {first_city}")
        return catalog_imgs[0]

    print(f"🌐 Hero via provedores externos: {first_city}")
    imgs = search_multiple_images(first_city, count=1)
    return imgs[0] if imgs else FALLBACK_IMAGE


def get_images_for_all_cities(destinations: List[str]) -> Dict[str, List[str]]:
    """
    Busca 3 imagens para cada cidade.
    Prioriza catálogo local, depois provedores externos.
    """
    result: Dict[str, List[str]] = {}

    for city in destinations:
        if not city:
            continue

        catalog_imgs = get_catalog_images(city, count=3)
        if catalog_imgs:
            print(f"📚 Catálogo: {city}")
            result[city] = catalog_imgs
            continue

        print(f"🌐 Provedores externos: {city}")
        result[city] = search_multiple_images(city, count=3)

    return result


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTE DE IMAGENS DE CIDADES (MULTIFONTE)")
    print("=" * 70)

    destinos_teste = ["Buenos Aires", "Lima", "São Paulo"]

    print("\n1) Testando hero image:")
    hero = get_hero_image_for_trip(destinos_teste)
    print(f"Hero: {hero}\n")

    print("\n2) Testando múltiplas imagens por cidade:")
    imagens = get_images_for_all_cities(destinos_teste)

    for cidade, urls in imagens.items():
        print(f"\n📍 {cidade}:")
        for i, url in enumerate(urls, 1):
            print(f"   Foto {i}: {url}")

    print("\n" + "=" * 70)
    print("✅ Teste concluído")

