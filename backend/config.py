"""
Configurações centralizadas do sistema de imagens e roteiros.
"""

from dataclasses import dataclass
from typing import Final


# ============================================================================
# CONFIGURAÇÕES DE IMAGENS
# ============================================================================

@dataclass(frozen=True)
class ImageSearchConfig:
    """Configurações para busca e processamento de imagens"""
    
    # URLs e Fallbacks
    FALLBACK_URL: str = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1200"
    
    # Limites de Busca
    CITY_IMAGES_LIMIT: int = 20
    
    # Pesos do Scoring (usado no fallback inteligente)
    CITY_NAME_BOOST: float = 2.0
    GENERIC_CITY_BOOST: float = 1.0
    LANDMARK_MATCH_BOOST: float = 2.0
    QUALITY_WEIGHT: float = 0.1
    
    # OpenAI Settings para Semantic Matching
    AI_MODEL: str = "gpt-4o"
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 50
    
    # Stopwords para normalização de texto
    STOPWORDS: tuple[str, ...] = (
        "cityscape",
        "foto da cidade de",
        "foto da cidade",
        "vista da cidade"
    )


# ============================================================================
# CONFIGURAÇÕES DE ROTEIRO
# ============================================================================

@dataclass(frozen=True)
class ItineraryConfig:
    """Configurações para geração de roteiros"""
    
    # OpenAI Settings
    AI_MODEL: str = "gpt-4o"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 3000
    
    # Timeouts e Retries
    API_TIMEOUT: int = 60
    MAX_RETRIES: int = 3
    
    # Validação
    MIN_DAYS: int = 1
    MAX_DAYS: int = 30


# ============================================================================
# INSTÂNCIAS GLOBAIS (IMUTÁVEIS)
# ============================================================================

IMAGE_CONFIG: Final = ImageSearchConfig()
ITINERARY_CONFIG: Final = ItineraryConfig()
