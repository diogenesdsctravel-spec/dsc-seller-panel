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
import logging
from typing import Optional, List, Dict, Any, Set
from supabase import create_client, Client
from openai import OpenAI

# Importar configurações
from config import IMAGE_CONFIG

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES
# ============================================================================

FALLBACK_URL = IMAGE_CONFIG.FALLBACK_URL


# ============================================================================
# VALIDAÇÃO
# ============================================================================

def _validate_string_input(value: Any, param_name: str) -> str:
    """
    Valida e normaliza input de string.
    
    Args:
        value: Valor a validar
        param_name: Nome do parâmetro (para mensagens de erro)
    
    Returns:
        String limpa e validada
    
    Raises:
        ValueError: Se valor for None ou vazio
        TypeError: Se valor não for string
    """
    if value is None:
        raise ValueError(f"{param_name} não pode ser None")
    
    if not isinstance(value, str):
        raise TypeError(
            f"{param_name} deve ser string, recebeu {type(value).__name__}"
        )
    
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{param_name} não pode ser vazio")
    
    return cleaned


# ============================================================================
# HELPERS
# ============================================================================

def _normalize(text: str) -> str:
    """Normaliza texto removendo stopwords e caracteres especiais"""
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    
    # Remove stopwords configuráveis
    for stopword in IMAGE_CONFIG.STOPWORDS:
        text = text.replace(stopword, "")
    
    # Mantém apenas letras, números e espaços
    cleaned = []
    for ch in text:
        if ch.isalnum() or ch.isspace():
            cleaned.append(ch)
    
    return "".join(cleaned).strip()


# ============================================================================
# IMAGE MANAGER CLASS
# ============================================================================

class ImageManager:
    """
    Gerenciador de imagens com dependencies injetadas.
    Permite testes e configuração flexível.
    """
    
    def __init__(
        self,
        supabase_client: Optional[Client] = None,
        openai_client: Optional[OpenAI] = None,
        config = IMAGE_CONFIG
    ):
        """
        Inicializa o ImageManager.
        
        Args:
            supabase_client: Cliente Supabase (opcional, será criado se None)
            openai_client: Cliente OpenAI (opcional, será criado se None)
            config: Configurações (padrão: IMAGE_CONFIG)
        """
        self.config = config
        self.db = supabase_client
        self.ai = openai_client
        
        # Lazy initialization
        if self.db is None:
            self.db = self._init_supabase()
        
        if self.ai is None:
            self.ai = self._init_openai()
    
    def _init_supabase(self) -> Optional[Client]:
        """Inicializa cliente Supabase"""
        url = os.getenv("SUPABASE_URL")
        key = (
            os.getenv("SUPABASE_ANON_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_KEY")
        )
        
        if not url or not key:
            logger.warning("⚠️ Variáveis SUPABASE não configuradas")
            return None
        
        try:
            client = create_client(url, key)
            logger.info("✅ Conexão com Supabase inicializada")
            return client
        except Exception as e:
            logger.error(f"❌ Erro ao conectar no Supabase: {e}")
            return None
    
    def _init_openai(self) -> Optional[OpenAI]:
        """Inicializa cliente OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("⚠️ OPENAI_API_KEY não configurada")
            return None
        
        try:
            return OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar OpenAI: {e}")
            return None
    
    def _buscar_qualquer_imagem_da_cidade(
        self, 
        city: str, 
        alvo_landmark: Optional[str] = None
    ) -> Optional[str]:
        """
        Fallback inteligente: pega QUALQUER imagem da cidade com melhor score.
        """
        if not self.db:
            return None

        try:
            result = (
                self.db.table("destination_images")
                .select("image_url, landmark, description, quality, created_at")
                .eq("city", city)
                .order("quality", desc=True)
                .order("created_at", desc=True)
                .limit(self.config.CITY_IMAGES_LIMIT)
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

                if city_norm and city_norm in texto_norm:
                    score += self.config.CITY_NAME_BOOST

                if any(palavra in texto_norm for palavra in ["buenos aires", "cidade", "panoramica", "panorâmica"]):
                    score += self.config.GENERIC_CITY_BOOST

                if alvo_norm and alvo_norm in texto_norm:
                    score += self.config.LANDMARK_MATCH_BOOST

                try:
                    q = float(row.get("quality") or 0)
                    score += q * self.config.QUALITY_WEIGHT
                except Exception:
                    pass

                if score > melhor_score:
                    melhor_score = score
                    melhor = row

            if melhor:
                logger.info(
                    f"💎 [SUPABASE CITY_FALLBACK] {city} - {melhor.get('landmark')} "
                    f"(score={melhor_score:.2f})"
                )
                return melhor.get("image_url")

            return None

        except Exception as e:
            logger.error(f"⚠️ Erro no fallback por cidade: {e}")
            return None
    
    def encontrar_landmark_semantico(
        self, 
        city: str, 
        landmark_buscado: str
    ) -> Optional[str]:
        """
        Usa IA para encontrar o landmark correto via matching semântico.
        """
        # Validação
        try:
            city = _validate_string_input(city, "city")
            landmark_buscado = _validate_string_input(landmark_buscado, "landmark_buscado")
        except (ValueError, TypeError) as e:
            logger.error(f"Input inválido: {e}")
            return None
        
        if not self.db:
            return None

        try:
            result = (
                self.db.table("destination_images")
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

            # Fast path
            if landmark_buscado in landmarks_disponiveis:
                return landmark_buscado

            if not self.ai:
                logger.warning("⚠️ OpenAI não disponível para matching semântico")
                return None

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

            response = self.ai.chat.completions.create(
                model=self.config.AI_MODEL,
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
                temperature=self.config.AI_TEMPERATURE,
                max_tokens=self.config.AI_MAX_TOKENS,
            )

            resultado = (response.choices[0].message.content or "").strip()

            if resultado in landmarks_disponiveis:
                logger.info(f"🤖 [IA MATCH] '{landmark_buscado}' → '{resultado}'")
                return resultado

            return None

        except Exception as e:
            logger.error(f"⚠️ Erro no matching semântico: {e}")
            return None
    
    def buscar_imagem(self, city: str, landmark: str) -> Optional[str]:
        """
        Busca imagem curada no Supabase com matching semântico via IA.
        """
        # Validação
        try:
            city = _validate_string_input(city, "city")
            landmark = _validate_string_input(landmark, "landmark")
        except (ValueError, TypeError) as e:
            logger.error(f"Input inválido: {e}")
            return None
        
        if not self.db:
            logger.error("Supabase não disponível")
            return None

        try:
            # 1) Match exato
            result = (
                self.db.table("destination_images")
                .select("image_url, description, landmark")
                .eq("city", city)
                .eq("landmark", landmark)
                .limit(1)
                .execute()
            )

            if result.data:
                img = result.data[0]
                logger.info(f"💎 [SUPABASE EXATO] {city} - {landmark}")
                desc = img.get("description")
                if desc:
                    logger.debug(f"   Desc: {desc[:60]}")
                return img.get("image_url")

            # 2) Matching semântico
            landmark_correto = self.encontrar_landmark_semantico(city, landmark)

            if landmark_correto:
                result = (
                    self.db.table("destination_images")
                    .select("image_url, description, landmark")
                    .eq("city", city)
                    .eq("landmark", landmark_correto)
                    .limit(1)
                    .execute()
                )

                if result.data:
                    img = result.data[0]
                    logger.info(
                        f"💎 [SUPABASE IA] {city} - {landmark_correto} "
                        f"(buscou: {landmark})"
                    )
                    desc = img.get("description")
                    if desc:
                        logger.debug(f"   Desc: {desc[:60]}")
                    return img.get("image_url")

            # 3) Fallback inteligente
            url = self._buscar_qualquer_imagem_da_cidade(city, alvo_landmark=landmark)
            if url:
                return url

            return None

        except Exception as e:
            logger.error(f"⚠️ Erro ao buscar no Supabase: {e}")
            return None
    
    def salvar_imagem(
        self,
        city: str,
        landmark: str,
        image_url: str,
        source: str = "auto",
        description: Optional[str] = None,
    ) -> bool:
        """Salva imagem no Supabase"""
        # Validação
        try:
            city = _validate_string_input(city, "city")
            landmark = _validate_string_input(landmark, "landmark")
            image_url = _validate_string_input(image_url, "image_url")
        except (ValueError, TypeError) as e:
            logger.error(f"Input inválido: {e}")
            return False
        
        if not self.db:
            logger.error("Supabase não disponível")
            return False

        try:
            existing_url = (
                self.db.table("destination_images")
                .select("id, landmark")
                .eq("image_url", image_url)
                .limit(1)
                .execute()
            )

            if existing_url.data:
                logger.warning(
                    f"⚠️ Esta URL já está cadastrada como: "
                    f"{existing_url.data[0]['landmark']}"
                )
                return False

            existing = (
                self.db.table("destination_images")
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
                    logger.info(f"ℹ️ Já existe '{landmark}', salvando como '{final_landmark}'")

            data = {
                "city": city,
                "landmark": final_landmark,
                "image_url": image_url,
                "source": source,
                "quality": 5 if source == "manual" else 4,
            }

            if description:
                data["description"] = description

            self.db.table("destination_images").insert(data).execute()
            logger.info(f"💾 Salvo no Supabase: {city} - {final_landmark}")
            return True

        except Exception as e:
            logger.error(f"⚠️ Erro ao salvar no Supabase: {e}")
            return False
    
    def get_hero_image_for_trip(self, destinations: List[str]) -> str:
        """Busca a imagem hero para o destino principal"""
        if not destinations:
            return FALLBACK_URL

        city = destinations[0]

        if not self.db:
            return FALLBACK_URL

        url = self._buscar_qualquer_imagem_da_cidade(city, alvo_landmark=f"{city} cityscape")
        if url:
            return url

        url = self.buscar_imagem(city, f"{city} cityscape")
        if url:
            return url

        return FALLBACK_URL
    
    def get_images_for_all_cities(self, destinations: List[str]) -> Dict[str, str]:
        """Busca imagens para todas as cidades da viagem"""
        images: Dict[str, str] = {}

        for city in destinations:
            if not city:
                continue

            url = self.buscar_imagem(city, f"{city} cityscape")
            if not url:
                url = FALLBACK_URL

            images[city] = url

        return images
    
    def listar_todas_imagens(self) -> List[Dict]:
        """Lista todas as imagens cadastradas"""
        if not self.db:
            return []

        try:
            result = (
                self.db.table("destination_images")
                .select("*")
                .order("city")
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"⚠️ Erro ao listar: {e}")
            return []


# ============================================================================
# INTERFACE DE COMPATIBILIDADE (mantém código legado funcionando)
# ============================================================================

# Instância global padrão
_default_manager: Optional[ImageManager] = None

def _get_manager() -> ImageManager:
    """Lazy singleton do manager"""
    global _default_manager
    if _default_manager is None:
        _default_manager = ImageManager()
    return _default_manager


# Funções legacy que delegam para o manager
def buscar_imagem(city: str, landmark: str) -> Optional[str]:
    """Wrapper para compatibilidade"""
    return _get_manager().buscar_imagem(city, landmark)


def encontrar_landmark_semantico(city: str, landmark_buscado: str) -> Optional[str]:
    """Wrapper para compatibilidade"""
    return _get_manager().encontrar_landmark_semantico(city, landmark_buscado)


def salvar_imagem(
    city: str,
    landmark: str,
    image_url: str,
    source: str = "auto",
    description: Optional[str] = None,
) -> bool:
    """Wrapper para compatibilidade"""
    return _get_manager().salvar_imagem(city, landmark, image_url, source, description)


def get_hero_image_for_trip(destinations: List[str]) -> str:
    """Wrapper para compatibilidade"""
    return _get_manager().get_hero_image_for_trip(destinations)


def get_images_for_all_cities(destinations: List[str]) -> Dict[str, str]:
    """Wrapper para compatibilidade"""
    return _get_manager().get_images_for_all_cities(destinations)


def listar_todas_imagens() -> List[Dict]:
    """Wrapper para compatibilidade"""
    return _get_manager().listar_todas_imagens()


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🧪 TESTE DE COMPATIBILIDADE")
    logger.info("=" * 70)

    logger.info("\n1️⃣ Teste com funções legacy (compatibilidade):")
    url = buscar_imagem("Buenos Aires", "Ponte da Mulher")
    logger.info(f"Legacy function → {url}\n")

    logger.info("2️⃣ Teste com ImageManager direto:")
    manager = ImageManager()
    url2 = manager.buscar_imagem("Buenos Aires", "Buenos Aires cityscape")
    logger.info(f"Manager class → {url2}\n")

    logger.info("3️⃣ Teste hero image:")
    hero = get_hero_image_for_trip(["Buenos Aires"])
    logger.info(f"Hero → {hero}\n")

    logger.info("=" * 70)
