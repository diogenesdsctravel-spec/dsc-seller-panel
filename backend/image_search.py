"""
Módulo para buscar imagens curadas no Supabase,
com suporte a matching semântico de landmarks via IA.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from typing import Optional, List

from supabase import create_client, Client
from openai import OpenAI

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
        print("✅ Conexão com Supabase inicializada em supabase_images")
    except Exception as e:
        print(f"⚠️ Erro ao conectar no Supabase em supabase_images: {e}")
        supabase = None
else:
    print("ℹ️ Variáveis SUPABASE_URL ou SUPABASE_KEY não configuradas")


def encontrar_landmark_semantico(city: str, landmark_buscado: str) -> Optional[str]:
    """
    Usa IA para encontrar o landmark correto no banco
    através de matching semântico.

    Exemplos:
    "Ponte da Mulher" → "Puerto Madero"
    "La Boca" → "Caminito"
    "Cemitério" → "Cemitério da Recoleta"
    """
    if not supabase:
        return None

    try:
        result = (
            supabase.table("destination_images")
            .select("landmark")
            .eq("city", city)
            .execute()
        )

        if not result.data or len(result.data) == 0:
            return None

        landmarks_disponiveis: List[str] = [
            x.get("landmark")
            for x in result.data
            if isinstance(x.get("landmark"), str)
        ]

        if not landmarks_disponiveis:
            return None

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
Identifique qual landmark disponível no banco corresponde ao landmark procurado.

REGRAS:
- "Ponte da Mulher" = "Puerto Madero" (a ponte fica lá)
- "La Boca" = "Caminito" (Caminito é em La Boca)
- "Cemitério" = "Cemitério da Recoleta"
- "Palermo" pode ser "Palermo" ou similar
- Se não houver correspondência clara, retorne "NENHUM"

Retorne APENAS o nome exato do landmark da lista, ou "NENHUM".
Não adicione explicações."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é especialista em associar landmarks. "
                        "Retorne APENAS o nome do landmark ou NENHUM."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=50,
        )

        resultado = (response.choices[0].message.content or "").strip()

        if resultado in landmarks_disponiveis:
            print(f"🤖 [IA MATCH] '{landmark_buscado}' → '{resultado}'")
            return resultado

        if resultado.upper() == "NENHUM":
            return None

        return None

    except Exception as e:
        print(f"⚠️ Erro no matching semântico: {e}")
        return None


def buscar_imagem(city: str, landmark: str) -> Optional[str]:
    """
    Busca imagem curada no Supabase com matching semântico via IA.

    Args:
        city: Nome da cidade, por exemplo "Buenos Aires"
        landmark: Nome do ponto, por exemplo "Ponte da Mulher"

    Returns:
        URL da imagem ou None se não encontrar
    """
    if not supabase:
        return None

    try:
        result = (
            supabase.table("destination_images")
            .select("image_url, description, landmark")
            .eq("city", city)
            .eq("landmark", landmark)
            .limit(1)
            .execute()
        )

        if result.data and len(result.data) > 0:
            img = result.data[0]
            print(f"💎 [SUPABASE EXATO] {city} - {landmark}")
            desc = img.get("description")
            if desc:
                print(f"   Desc: {desc[:50]}")
            return img.get("image_url")

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

            if result.data and len(result.data) > 0:
                img = result.data[0]
                print(
                    f"💎 [SUPABASE IA] {city} - {landmark_correto} "
                    f"(buscou: {landmark})"
                )
                desc = img.get("description")
                if desc:
                    print(f"   Desc: {desc[:50]}")
                return img.get("image_url")

        return None

    except Exception as e:
        print(f"⚠️ Erro ao buscar no Supabase: {e}")
        return None


if __name__ == "__main__":
    print("🧪 Teste rápido do módulo supabase_images")

    exemplo_city = "Buenos Aires"
    exemplo_landmark = "Ponte da Mulher"

    url = buscar_imagem(exemplo_city, exemplo_landmark)
    print(f"Resultado para {exemplo_city} - {exemplo_landmark}: {url}")
