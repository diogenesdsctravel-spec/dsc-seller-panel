"""
Módulo para gerenciar imagens de destinos turísticos.

Responsabilidades:
- Buscar imagens curadas no Supabase
- Matching semântico de landmarks via OpenAI
- Salvar novas imagens no banco
- Funções auxiliares para extração de dados de viagens

Single source of truth para todas as operações com imagens.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from openai import OpenAI

# ============================================================================

FALLBACK_URL = (
    "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200"
)

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = (
    os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_KEY")
)

supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Conexão com Supabase inicializada")
    except Exception as e:
        print(f"⚠️ Erro ao conectar no Supabase: {e}")
        supabase = None
else:
    print("ℹ️ Variáveis SUPABASE_URL ou SUPABASE_KEY não configuradas")


# ============================================================================
# HELPERS INTERNOS
# ============================================================================

def _normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # remove palavras muito genéricas que atrapalham a comparação
    for lixo in ["cityscape", "foto da cidade de", "foto da cidade", "vista da cidade"]:
        text = text.replace(lixo, "")
    # mantém apenas letras, números e espaços
    cleaned = []
    for ch in text:
        if ch.isalnum() or ch.isspace():
            cleaned.append(ch)
    return "".join(cleaned).strip()


def _buscar_qualquer_imagem_da_cidade(city: str, alvo_landmark: str | None = None) -> Optional[str]:
    """
    Fallback inteligente: se não achar o landmark exato/semântico,
    pega QUALQUER imagem da cidade, priorizando a que mais parece
    representar a cidade (cidade no texto, qualidade maior, etc).

    Nunca usa Unsplash aqui – só navega dentro do banco.
    """
    if not supabase:
        return None

    try:
        result = (
            supabase.table("destination_images")
            .select("image_url, landmark, description, quality, created_at")
            .eq("city", city)
            .order("quality", desc=True)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )

        rows: List[Dict[str, Any]] = result.data or []
        if not rows:
            return None

        alvo_norm = _normalize(alvo_landmark or "")
        city_norm = _normalize(city)

        melhor = None
        melhor_score = -1.0

        for row in rows:
            landmark = row.get("landmark") or ""
            desc = row.get("description") or ""
            texto = f"{landmark} {desc}"
            texto_norm = _normalize(texto)

            score = 0.0

            # se contiver o nome da cidade, já é bem relevante
            if city_norm and city_norm in texto_norm:
                score += 2.0

            # se parecer uma foto "da cidade" (genérica panorâmica)
            if any(palavra in texto_norm for palavra in ["buenos aires", "cidade", "panoramica", "panorâmica"]):
                score += 1.0

            # se o alvo do dia tiver alguma relação textual
            if alvo_norm and alvo_norm in texto_norm:
                score += 2.0

            # qualidade como pequeno peso extra
            try:
                q = float(row.get("quality") or 0)
                score += q / 10.0
            except Exception:
                pass

            if score > melhor_score:
                melhor_score = score
                melhor = row

        if melhor:
            print(
                f"💎 [SUPABASE CITY_FALLBACK] {city} - {melhor.get('landmark')} "
                f"(score={melhor_score:.2f})"
            )
            return melhor.get("image_url")

        return None

    except Exception as e:
        print(f"⚠️ Erro no fallback por cidade: {e}")
        return None


# ============================================================================
# BUSCA E MATCHING SEMÂNTICO
# ============================================================================

def encontrar_landmark_semantico(city: str, landmark_buscado: str) -> Optional[str]:
    """
    Usa IA para encontrar o landmark correto no banco através de matching semântico.

    Exemplos:
        "Ponte da Mulher" → "Puerto Madero"
        "La Boca" → "Caminito"
        "Cemitério" → "Cemitério da Recoleta"
        "Buenos Aires cityscape" → "Buenos Aires"

    Se não achar correspondência forte, retorna None.
    """
    if not supabase:
        return None

    try:
        result = (
            supabase.table("destination_images")
            .select("landmark, description")
            .eq("city", city)
            .execute()
        )

        if not result.data:
            return None

        landmarks_disponiveis: List[str] = []
        for x in result.data:
            nome = x.get("landmark")
            if isinstance(nome, str):
                landmarks_disponiveis.append(nome)

        if not landmarks_disponiveis:
            return None

        # Fast path simples
        if landmark_buscado in landmarks_disponiveis:
            return landmark_buscado

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("ℹ️ OPENAI_API_KEY não configurada para matching semântico")
            return None

        client = OpenAI(api_key=api_key)
        lista_formatada = "\n".join([f"- {l}" for l in landmarks_disponiveis])

        prompt = f"""Você é um especialista em pontos turísticos.

CIDADE: {city}
LANDMARK PROCURADO: {landmark_buscado}

LANDMARKS DISPONÍVEIS NO BANCO:
{lista_formatada}

TAREFA:
Escolha qual landmark disponível corresponde melhor ao procurado.

REGRAS ESPECIAIS:
- "Ponte da Mulher" = "Puerto Madero" (a ponte fica lá)
- "La Boca" = "Caminito"
- "Cemitério" = "Cemitério da Recoleta"
- Se o procurado for algo como "NOMEDACIDADE cityscape", "foto da cidade",
  "vista da cidade", "foto geral da cidade", escolha o landmark que
  representa a própria cidade (ex: "Buenos Aires").
- Se NÃO houver correspondência clara com NENHUM da lista, responda "NENHUM".

Retorne APENAS o nome exato do landmark da lista, ou "NENHUM"."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é especialista em associar landmarks. "
                        "Responda APENAS com o nome de um landmark da lista ou NENHUM."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=50,
        )

        resultado = (response.choices[0].message.content or "").strip()

        if resultado in landmarks_disponiveis:
            print(f"🤖 [IA MATCH] '{landmark_buscado}' → '{resultado}'")
            return resultado

        return None

    except Exception as e:
        print(f"⚠️ Erro no matching semântico: {e}")
        return None


def buscar_imagem(city: str, landmark: str) -> Optional[str]:
    """
    Busca imagem curada no Supabase com matching semântico via IA.

    Fluxo:
    1. Tenta match exato (city + landmark)
    2. Se falhar, usa IA para matching semântico dentro dos landmarks da cidade
    3. Se ainda assim falhar, pega QUALQUER imagem da cidade com melhor score
       (nunca cai em fallback externo se houver alguma foto da cidade)
    4. Só retorna None se não houver NENHUMA foto daquela cidade no banco
       ou se o Supabase estiver indisponível.
    """
    if not supabase:
        return None

    try:
        # 1) Match exato
        result = (
            supabase.table("destination_images")
            .select("image_url, description, landmark")
            .eq("city", city)
            .eq("landmark", landmark)
            .limit(1)
            .execute()
        )

        if result.data:
            img = result.data[0]
            print(f"💎 [SUPABASE EXATO] {city} - {landmark}")
            desc = img.get("description")
            if desc:
                print(f"   Desc: {desc[:60]}")
            return img.get("image_url")

        # 2) Matching semântico (landmark → outro já cadastrado)
        landmark_correto = encontrar_landmark_semantico(city, landmark)

        if landmark_correto:
            result = (
                supabase.table("destination_images")
                .select("image_url, description, landmark")
                .eq("city", city)
                .eq("landmark", landmark_correto)
                .limit(1)
                .execute()
            )

            if result.data:
                img = result.data[0]
                print(
                    f"💎 [SUPABASE IA] {city} - {landmark_correto} "
                    f"(buscou: {landmark})"
                )
                desc = img.get("description")
                if desc:
                    print(f"   Desc: {desc[:60]}")
                return img.get("image_url")

        # 3) Fallback inteligente: qualquer imagem da cidade
        url = _buscar_qualquer_imagem_da_cidade(city, alvo_landmark=landmark)
        if url:
            return url

        # Nenhuma foto da cidade – deixa quem chamou decidir o fallback externo
        return None

    except Exception as e:
        print(f"⚠️ Erro ao buscar no Supabase: {e}")
        return None


# ============================================================================
# SALVAR IMAGENS
# ============================================================================

def salvar_imagem(
    city: str,
    landmark: str,
    image_url: str,
    source: str = "auto",
    description: str | None = None,
) -> bool:
    """
    Salva imagem no Supabase.
    Se já existir foto do mesmo landmark, cria variação com sufixo numérico.
    """
    if not supabase:
        return False

    try:
        existing_url = (
            supabase.table("destination_images")
            .select("id, landmark")
            .eq("image_url", image_url)
            .limit(1)
            .execute()
        )

        if existing_url.data:
            print(
                "⚠️ Esta URL já está cadastrada como: "
                f"{existing_url.data[0]['landmark']}"
            )
            return False

        existing = (
            supabase.table("destination_images")
            .select("landmark")
            .eq("city", city)
            .ilike("landmark", f"{landmark}%")
            .execute()
        )

        final_landmark = landmark
        if existing.data:
            count = len(
                [x for x in existing.data if str(x.get("landmark", "")).startswith(landmark)]
            )
            if count > 0:
                final_landmark = f"{landmark} {count + 1}"
                print(f"ℹ️ Já existe '{landmark}', salvando como '{final_landmark}'")

        data = {
            "city": city,
            "landmark": final_landmark,
            "image_url": image_url,
            "source": source,
            "quality": 5 if source == "manual" else 4,
        }

        if description:
            data["description"] = description

        supabase.table("destination_images").insert(data).execute()
        print(f"💾 Salvo no Supabase: {city} - {final_landmark}")
        return True

    except Exception as e:
        print(f"⚠️ Erro ao salvar no Supabase: {e}")
        return False


# ============================================================================
# FUNÇÕES AUXILIARES PARA VIAGENS
# ============================================================================

def get_hero_image_for_trip(destinations: List[str]) -> Optional[str]:
    """
    Busca a imagem hero para o destino principal da viagem.

    Regra:
    - Se existir QUALQUER imagem daquela cidade no banco, usa ela
      (priorizando fotos que parecem representar a cidade).
    - Só usa FALLBACK_URL se:
        a) não houver nenhuma imagem para a cidade, ou
        b) o Supabase estiver indisponível.
    """
    if not destinations:
        return FALLBACK_URL

    city = destinations[0]

    # Se Supabase estiver fora, não temos o que fazer
    if not supabase:
        return FALLBACK_URL

    # Tentar pegar uma imagem que represente bem a cidade
    url = _buscar_qualquer_imagem_da_cidade(city, alvo_landmark=f"{city} cityscape")
    if url:
        return url

    # Se não houver nada da cidade, ainda tentamos via buscar_imagem (que também usa banco)
    url = buscar_imagem(city, f"{city} cityscape")
    if url:
        return url

    # Último caso: realmente não há nada no banco
    return FALLBACK_URL


def get_images_for_all_cities(destinations: List[str]) -> Dict[str, str]:
    """
    Busca imagens para todas as cidades da viagem.

    Para cada cidade:
    - tenta pegar alguma imagem curada (nunca genérica se a cidade tiver foto)
    - só coloca fallback se a cidade não tiver NENHUMA foto no banco
    """
    images: Dict[str, str] = {}

    for city in destinations:
        if not city:
            continue

        url = buscar_imagem(city, f"{city} cityscape")
        if not url:
            # Não há nada no banco para essa cidade
            url = FALLBACK_URL

        images[city] = url

    return images


# ============================================================================
# UTILITÁRIOS
# ============================================================================

def listar_todas_imagens() -> List[Dict]:
    """
    Lista todas as imagens cadastradas.
    """
    if not supabase:
        return []

    try:
        result = (
            supabase.table("destination_images")
            .select("*")
            .order("city")
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"⚠️ Erro ao listar: {e}")
        return []


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTE DE CONEXÃO E FUNCIONALIDADES")
    print("=" * 70)

    print("\n1️⃣ Teste de busca com matching semântico:")
    url = buscar_imagem("Buenos Aires", "Ponte da Mulher")
    print(f"Resultado Ponte da Mulher → {url}\n")

    print("2️⃣ Teste de cityscape → cidade:")
    url2 = buscar_imagem("Buenos Aires", "Buenos Aires cityscape")
    print(f"Resultado BA cityscape → {url2}\n")

    print("3️⃣ Teste de imagem hero:")
    hero = get_hero_image_for_trip(["Buenos Aires", "Lima"])
    print(f"Hero image: {hero}\n")

    print("4️⃣ Teste de múltiplas cidades:")
    images = get_images_for_all_cities(["Buenos Aires", "Lima", "Cusco"])
    for c, u in images.items():
        print(f"  {c}: {u[:60]}...")

    print("\n" + "=" * 70)
