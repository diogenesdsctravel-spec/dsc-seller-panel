"""
Gera roteiro dia-a-dia usando OpenAI GPT-4.

Arquitetura:
- TripDataExtractor: Extrai e valida dados da viagem
- PromptBuilder: Constrói prompts para a IA
- ResponseProcessor: Processa e valida respostas da IA
- ItineraryGenerator: Orquestra tudo
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
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


# ============================================================================
# DATA EXTRACTOR
# ============================================================================

class TripDataExtractor:
    """Extrai e valida dados da viagem"""
    
    @staticmethod
    def extract_main_city(trip_data: dict) -> str:
        """
        Extrai cidade principal da viagem.
        
        Tenta em ordem:
        1. Primeiro hotel
        2. Destino do primeiro voo
        3. Fallback para cidade padrão
        """
        # Tentar hotéis
        hoteis = trip_data.get("hoteis", [])
        if hoteis and len(hoteis) > 0:
            cidade = hoteis[0].get("cidade", "")
            if cidade:
                logger.debug(f"Cidade extraída de hotéis: {cidade}")
                return cidade
        
        # Tentar voos
        voos = trip_data.get("voos", [])
        if voos and len(voos) > 0:
            destino = voos[0].get("destino", "")
            if destino and "(" in destino:
                # Extrair cidade de "Buenos Aires (AEP)"
                cidade = destino.split("(")[0].strip()
                logger.debug(f"Cidade extraída de voos: {cidade}")
                return cidade
        
        logger.warning(
            f"Não foi possível determinar cidade, "
            f"usando padrão: {ITINERARY_CONFIG.DEFAULT_CITY}"
        )
        return ITINERARY_CONFIG.DEFAULT_CITY
    
    @staticmethod
    def has_transfer(trip_data: dict) -> bool:
        """Verifica se há transfer incluído"""
        passeios = trip_data.get("passeios", [])
        return any(
            "transfer" in str(p.get("nome", "")).lower() 
            for p in passeios
        )
    
    @staticmethod
    def get_period(trip_data: dict) -> tuple[str, str]:
        """Retorna datas de início e fim"""
        periodo = trip_data.get("periodo", {})
        inicio = periodo.get("inicio", "")
        fim = periodo.get("fim", "")
        return inicio, fim


# ============================================================================
# PROMPT BUILDER
# ============================================================================

class PromptBuilder:
    """Constrói prompts para a IA"""
    
    @staticmethod
    def build_itinerary_prompt(
        cidade: str,
        inicio: str,
        fim: str,
        voos: List[dict],
        hoteis: List[dict],
        passeios: List[dict],
        tem_transfer: bool
    ) -> str:
        """
        Constrói o prompt principal para geração de roteiro.
        
        Args:
            cidade: Cidade principal
            inicio: Data de início
            fim: Data de fim
            voos: Lista de voos
            hoteis: Lista de hotéis
            passeios: Lista de passeios
            tem_transfer: Se tem transfer incluído
        
        Returns:
            Prompt formatado
        """
        landmarks_texto = LANDMARK_DB.get_landmarks_text(cidade)
        transfer_status = "incluido" if tem_transfer else "a-incluir"
        
        return f"""Crie um roteiro dia-a-dia COMPLETO para esta viagem a {cidade}:

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
   - Dia 1 (chegada): use "{cidade} cityscape"
   - Último dia (partida): use "{cidade} airport"

2. DIA DE CHEGADA (Dia 1):
   - Título: "Chegada a {cidade}"
   - landmark: "{cidade} cityscape"
   - Horário: Mostrar horário de chegada do voo
   - Descrição: 2-3 parágrafos sobre chegada, transfer, check-in e primeira noite
   - Transfer: "{transfer_status}"
   - Dica: Uma dica prática sobre o bairro do hotel

3. DIAS INTERMEDIÁRIOS (Dia 2 até penúltimo):
   - Título: Nome de atividade/bairro
   - landmark: Nome DO LOCAL específico visitado
   - Descrição: 2-3 parágrafos com sugestões de manhã, tarde e noite
   - VARIE os bairros/locais a cada dia
   - Se tem passeio incluído: mencionar "✓ [Nome do passeio] incluído"
   - Dica: Dica sobre restaurantes, horários, transporte

4. DIA DE PARTIDA (Último dia):
   - Título: "Retorno"
   - landmark: "{cidade} airport"
   - Horário: Mostrar horário do voo de volta
   - Descrição: Check-out, transfer ao aeroporto, despedida
   - Transfer: "{transfer_status}"
   - Dica: Dica sobre check-in antecipado

LANDMARKS VÁLIDOS PARA {cidade}:
{landmarks_texto}

FORMATO JSON (retorne APENAS JSON array limpo, sem ```json):
[
  {{
    "dia": 1,
    "data": "{inicio}",
    "titulo": "Chegada a {cidade}",
    "landmark": "{cidade} cityscape",
    "horario": "Chegada às XX:XX",
    "descricao": "...",
    "transfer": "{transfer_status}",
    "dica": "..."
  }}
]

IMPORTANTE: CADA DIA DEVE TER UM LANDMARK DIFERENTE para garantir variedade visual nas fotos!"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Retorna o prompt do sistema"""
        return (
            "Você é um especialista em roteiros de viagem. "
            "Crie roteiros detalhados, práticos e inspiradores. "
            "SEMPRE inclua o campo 'landmark' em cada dia. "
            "Retorne APENAS JSON array limpo, sem markdown."
        )


# ============================================================================
# RESPONSE PROCESSOR
# ============================================================================

class ResponseProcessor:
    """Processa e valida respostas da IA"""
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        """
        Remove markdown wrapper se presente.
        
        Args:
            text: Texto da resposta
        
        Returns:
            Texto limpo
        """
        text = text.strip()
        
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove primeira e última linha (```json e ```)
            text = "\n".join(lines[1:-1])
        
        return text.strip()
    
    @staticmethod
    def parse_json(text: str) -> List[dict]:
        """
        Parse JSON com tratamento de erro.
        
        Args:
            text: String JSON
        
        Returns:
            Lista de dicionários
        
        Raises:
            json.JSONDecodeError: Se JSON inválido
            ValueError: Se não for lista
        """
        try:
            data = json.loads(text)
            
            if not isinstance(data, list):
                raise ValueError(f"Esperado lista, recebeu {type(data).__name__}")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido: {e}")
            raise
    
    @staticmethod
    def validate_itinerary(
        dias: List[dict],
        cidade: str
    ) -> List[dict]:
        """
        Valida estrutura do roteiro e adiciona landmarks ausentes.
        
        Args:
            dias: Lista de dias do roteiro
            cidade: Cidade principal
        
        Returns:
            Lista validada
        """
        # Validar número de dias
        if len(dias) < ITINERARY_CONFIG.MIN_DAYS:
            raise ValueError(
                f"Roteiro muito curto: {len(dias)} dias "
                f"(mínimo: {ITINERARY_CONFIG.MIN_DAYS})"
            )
        
        if len(dias) > ITINERARY_CONFIG.MAX_DAYS:
            logger.warning(
                f"Roteiro longo: {len(dias)} dias "
                f"(máximo recomendado: {ITINERARY_CONFIG.MAX_DAYS})"
            )
        
        # Validar e corrigir landmarks
        for dia in dias:
            if "landmark" not in dia or not dia["landmark"]:
                dia_num = dia.get("dia", 0)
                
                # Determinar landmark padrão baseado no dia
                if dia_num == 1:
                    landmark = f"{cidade} cityscape"
                elif dia_num == len(dias):
                    landmark = f"{cidade} airport"
                else:
                    landmark = f"{cidade} cityscape"
                
                dia["landmark"] = landmark
                logger.warning(
                    f"Dia {dia_num} sem landmark, "
                    f"adicionado: {landmark}"
                )
        
        return dias


# ============================================================================
# ITINERARY GENERATOR
# ============================================================================

class ItineraryGenerator:
    """Gerador de roteiros com IA"""
    
    def __init__(
        self,
        openai_client: Optional[OpenAI] = None,
        config = ITINERARY_CONFIG
    ):
        """
        Inicializa o gerador.
        
        Args:
            openai_client: Cliente OpenAI (opcional)
            config: Configurações (padrão: ITINERARY_CONFIG)
        """
        self.config = config
        self.ai = openai_client
        
        if self.ai is None:
            self.ai = self._init_openai()
    
    def _init_openai(self) -> Optional[OpenAI]:
        """Inicializa cliente OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("❌ OPENAI_API_KEY não configurada")
            return None
        
        try:
            return OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar OpenAI: {e}")
            return None
    
    def generate(self, trip_data: dict) -> List[dict]:
        """
        Gera roteiro completo para a viagem.
        
        Args:
            trip_data: Dados extraídos da viagem
        
        Returns:
            Lista de dias do roteiro
        
        Raises:
            RuntimeError: Se OpenAI não disponível
            ValueError: Se dados inválidos
        """
        if not self.ai:
            raise RuntimeError("OpenAI não disponível")
        
        # 1. Extrair dados
        cidade = TripDataExtractor.extract_main_city(trip_data)
        tem_transfer = TripDataExtractor.has_transfer(trip_data)
        inicio, fim = TripDataExtractor.get_period(trip_data)
        
        voos = trip_data.get("voos", [])
        hoteis = trip_data.get("hoteis", [])
        passeios = trip_data.get("passeios", [])
        
        # 2. Construir prompt
        prompt = PromptBuilder.build_itinerary_prompt(
            cidade=cidade,
            inicio=inicio,
            fim=fim,
            voos=voos,
            hoteis=hoteis,
            passeios=passeios,
            tem_transfer=tem_transfer
        )
        
        system_prompt = PromptBuilder.get_system_prompt()
        
        # 3. Chamar API
        logger.info(f"🤖 Gerando roteiro para {cidade}...")
        
        try:
            response = self.ai.chat.completions.create(
                model=self.config.AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.AI_TEMPERATURE,
                max_tokens=self.config.AI_MAX_TOKENS,
                timeout=self.config.API_TIMEOUT
            )
            
            result_text = response.choices[0].message.content.strip()
            
            logger.info(f"✅ Resposta recebida ({len(result_text)} caracteres)")
            
        except Exception as e:
            logger.error(f"❌ Erro na API OpenAI: {e}")
            raise RuntimeError(f"Falha ao gerar roteiro: {e}")
        
        # 4. Processar resposta
        try:
            cleaned = ResponseProcessor.clean_markdown(result_text)
            dias = ResponseProcessor.parse_json(cleaned)
            dias_validated = ResponseProcessor.validate_itinerary(dias, cidade)
            
            logger.info(f"✅ Roteiro gerado com {len(dias_validated)} dias")
            
            return dias_validated
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar resposta: {e}")
            raise


# ============================================================================
# INTERFACE DE COMPATIBILIDADE
# ============================================================================

_default_generator: Optional[ItineraryGenerator] = None

def _get_generator() -> ItineraryGenerator:
    """Lazy singleton do generator"""
    global _default_generator
    if _default_generator is None:
        _default_generator = ItineraryGenerator()
    return _default_generator


def generate_itinerary(trip_data: dict) -> list[dict]:
    """
    Wrapper para compatibilidade com código legado.
    
    Args:
        trip_data: Dados da viagem
    
    Returns:
        Lista de dias do roteiro
    """
    try:
        generator = _get_generator()
        return generator.generate(trip_data)
    except Exception as e:
        logger.error(f"❌ Erro ao gerar roteiro: {e}")
        return []


# ============================================================================
# TESTES
# ============================================================================

if __name__ == "__main__":
    test_data = {
        "periodo": {"inicio": "30/01", "fim": "06/02"},
        "voos": [
            {"origem": "VDC", "destino": "Buenos Aires (AEP)", "horario_chegada": "17:00", "data": "30/01"},
            {"origem": "Buenos Aires (EZE)", "destino": "VDC", "horario_saida": "02:30", "data": "06/02"}
        ],
        "hoteis": [
            {"cidade": "Buenos Aires", "nome": "Waldorf Hotel", "noites": 7}
        ],
        "passeios": []
    }
    
    logger.info("=" * 70)
    logger.info("🧪 TESTE COM ARQUITETURA REFATORADA")
    logger.info("=" * 70)
    
    # Teste com função legacy
    logger.info("\n1️⃣ Teste com função legacy (compatibilidade):")
    roteiro = generate_itinerary(test_data)
    if roteiro:
        logger.info(f"✅ {len(roteiro)} dias - Landmarks: {[d.get('landmark') for d in roteiro]}")
    
    # Teste com classe direta
    logger.info("\n2️⃣ Teste com ItineraryGenerator direto:")
    generator = ItineraryGenerator()
    roteiro2 = generator.generate(test_data)
    if roteiro2:
        logger.info(f"✅ {len(roteiro2)} dias gerados")
    
    logger.info("\n" + "=" * 70)
