"""
Testes unitários para generate_itinerary.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from generate_itinerary import (
    ItineraryGenerator,
    TripDataExtractor,
    PromptBuilder,
    ResponseProcessor,
    generate_itinerary
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_openai():
    """Mock do cliente OpenAI"""
    mock = MagicMock()
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = '''[
        {
            "dia": 1,
            "data": "30/01",
            "titulo": "Chegada a Buenos Aires",
            "landmark": "Buenos Aires cityscape",
            "horario": "17:00",
            "descricao": "Chegada",
            "transfer": "incluido",
            "dica": "Dica"
        }
    ]'''
    mock.chat.completions.create.return_value = response
    return mock


@pytest.fixture
def sample_trip_data():
    """Dados de viagem de exemplo"""
    return {
        "periodo": {"inicio": "30/01", "fim": "06/02"},
        "voos": [
            {
                "origem": "VDC",
                "destino": "Buenos Aires (AEP)",
                "horario_chegada": "17:00",
                "data": "30/01"
            }
        ],
        "hoteis": [
            {
                "cidade": "Buenos Aires",
                "nome": "Waldorf Hotel",
                "noites": 7
            }
        ],
        "passeios": [
            {"nome": "Transfer Aeroporto"}
        ]
    }


# ============================================================================
# TESTES DO TRIP DATA EXTRACTOR
# ============================================================================

class TestTripDataExtractor:
    """Testes do extrator de dados"""
    
    def test_extract_city_from_hotels(self, sample_trip_data):
        """Teste extração de cidade de hotéis"""
        city = TripDataExtractor.extract_main_city(sample_trip_data)
        assert city == "Buenos Aires"
    
    def test_extract_city_from_flights(self):
        """Teste extração de cidade de voos"""
        data = {
            "voos": [{"destino": "Lima (LIM)"}],
            "hoteis": []
        }
        city = TripDataExtractor.extract_main_city(data)
        assert city == "Lima"
    
    def test_extract_city_default(self):
        """Teste fallback para cidade padrão"""
        city = TripDataExtractor.extract_main_city({})
        assert city == "Buenos Aires"  # DEFAULT_CITY
    
    def test_has_transfer_true(self, sample_trip_data):
        """Teste detecção de transfer incluído"""
        has_transfer = TripDataExtractor.has_transfer(sample_trip_data)
        assert has_transfer is True
    
    def test_has_transfer_false(self):
        """Teste sem transfer"""
        data = {"passeios": [{"nome": "City Tour"}]}
        has_transfer = TripDataExtractor.has_transfer(data)
        assert has_transfer is False
    
    def test_get_period(self, sample_trip_data):
        """Teste extração de período"""
        inicio, fim = TripDataExtractor.get_period(sample_trip_data)
        assert inicio == "30/01"
        assert fim == "06/02"


# ============================================================================
# TESTES DO PROMPT BUILDER
# ============================================================================

class TestPromptBuilder:
    """Testes do construtor de prompts"""
    
    def test_build_prompt_contains_city(self):
        """Teste se prompt contém a cidade"""
        prompt = PromptBuilder.build_itinerary_prompt(
            cidade="Buenos Aires",
            inicio="30/01",
            fim="06/02",
            voos=[],
            hoteis=[],
            passeios=[],
            tem_transfer=False
        )
        assert "Buenos Aires" in prompt
    
    def test_build_prompt_contains_dates(self):
        """Teste se prompt contém as datas"""
        prompt = PromptBuilder.build_itinerary_prompt(
            cidade="Lima",
            inicio="01/03",
            fim="10/03",
            voos=[],
            hoteis=[],
            passeios=[],
            tem_transfer=False
        )
        assert "01/03" in prompt
        assert "10/03" in prompt
    
    def test_build_prompt_transfer_included(self):
        """Teste prompt com transfer incluído"""
        prompt = PromptBuilder.build_itinerary_prompt(
            cidade="Lima",
            inicio="01/03",
            fim="10/03",
            voos=[],
            hoteis=[],
            passeios=[],
            tem_transfer=True
        )
        assert "incluido" in prompt
    
    def test_build_prompt_transfer_not_included(self):
        """Teste prompt sem transfer"""
        prompt = PromptBuilder.build_itinerary_prompt(
            cidade="Lima",
            inicio="01/03",
            fim="10/03",
            voos=[],
            hoteis=[],
            passeios=[],
            tem_transfer=False
        )
        assert "a-incluir" in prompt
    
    def test_system_prompt_not_empty(self):
        """Teste se system prompt não é vazio"""
        prompt = PromptBuilder.get_system_prompt()
        assert len(prompt) > 0
        assert "especialista" in prompt.lower()


# ============================================================================
# TESTES DO RESPONSE PROCESSOR
# ============================================================================

class TestResponseProcessor:
    """Testes do processador de respostas"""
    
    def test_clean_markdown_with_wrapper(self):
        """Teste remoção de wrapper markdown"""
        text = "```json\n[{\"dia\": 1}]\n```"
        cleaned = ResponseProcessor.clean_markdown(text)
        assert cleaned == '[{"dia": 1}]'
    
    def test_clean_markdown_without_wrapper(self):
        """Teste texto sem markdown"""
        text = '[{"dia": 1}]'
        cleaned = ResponseProcessor.clean_markdown(text)
        assert cleaned == '[{"dia": 1}]'
    
    def test_parse_json_valid(self):
        """Teste parse de JSON válido"""
        text = '[{"dia": 1}, {"dia": 2}]'
        result = ResponseProcessor.parse_json(text)
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_parse_json_invalid(self):
        """Teste parse de JSON inválido"""
        with pytest.raises(Exception):
            ResponseProcessor.parse_json("invalid json")
    
    def test_parse_json_not_list(self):
        """Teste se não for lista"""
        with pytest.raises(ValueError, match="Esperado lista"):
            ResponseProcessor.parse_json('{"dia": 1}')
    
    def test_validate_itinerary_adds_missing_landmark(self):
        """Teste adição de landmark ausente"""
        dias = [
            {"dia": 1, "titulo": "Dia 1"},
            {"dia": 2, "titulo": "Dia 2", "landmark": "Obelisco"}
        ]
        validated = ResponseProcessor.validate_itinerary(dias, "Buenos Aires")
        
        assert "landmark" in validated[0]
        assert validated[0]["landmark"] == "Buenos Aires cityscape"
    
    def test_validate_itinerary_too_short(self):
        """Teste roteiro muito curto"""
        with pytest.raises(ValueError, match="muito curto"):
            ResponseProcessor.validate_itinerary([], "Buenos Aires")
    
    def test_validate_itinerary_airport_landmark(self):
        """Teste landmark de aeroporto no último dia"""
        dias = [
            {"dia": 1, "landmark": "cityscape"},
            {"dia": 2, "landmark": "Obelisco"},
            {"dia": 3}  # sem landmark
        ]
        validated = ResponseProcessor.validate_itinerary(dias, "Lima")
        
        # Último dia sem landmark deve receber "Lima airport"
        assert validated[2]["landmark"] == "Lima airport"


# ============================================================================
# TESTES DO ITINERARY GENERATOR
# ============================================================================

class TestItineraryGenerator:
    """Testes do gerador principal"""
    
    def test_init_with_client(self, mock_openai):
        """Teste inicialização com cliente fornecido"""
        generator = ItineraryGenerator(openai_client=mock_openai)
        assert generator.ai is mock_openai
    
    def test_generate_success(self, mock_openai, sample_trip_data):
        """Teste geração bem-sucedida"""
        generator = ItineraryGenerator(openai_client=mock_openai)
        result = generator.generate(sample_trip_data)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["landmark"] == "Buenos Aires cityscape"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_generate_without_api_key(self, sample_trip_data):
        """Teste sem API key"""
        generator = ItineraryGenerator(openai_client=None)
        
        with pytest.raises(RuntimeError, match="OpenAI não disponível"):
            generator.generate(sample_trip_data)


# ============================================================================
# TESTES DE COMPATIBILIDADE
# ============================================================================

class TestCompatibility:
    """Testes da função legacy"""
    
    @patch('generate_itinerary._get_generator')
    def test_generate_itinerary_legacy(self, mock_get_generator, sample_trip_data):
        """Teste função legacy"""
        mock_generator = Mock()
        mock_generator.generate.return_value = [
            {"dia": 1, "landmark": "Test"}
        ]
        mock_get_generator.return_value = mock_generator
        
        result = generate_itinerary(sample_trip_data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_generator.generate.assert_called_once()
    
    @patch('generate_itinerary._get_generator')
    def test_generate_itinerary_error_handling(self, mock_get_generator, sample_trip_data):
        """Teste tratamento de erro na função legacy"""
        mock_generator = Mock()
        mock_generator.generate.side_effect = Exception("Test error")
        mock_get_generator.return_value = mock_generator
        
        result = generate_itinerary(sample_trip_data)
        
        # Deve retornar lista vazia em caso de erro
        assert result == []
