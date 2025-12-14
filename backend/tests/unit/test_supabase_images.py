"""
Testes unitários para supabase_images.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from supabase_images import (
    ImageManager,
    buscar_imagem,
    buscar_imagem_para_dia,
    _validate_string_input,
    _normalize,
    FALLBACK_URL
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_supabase():
    """Mock do cliente Supabase"""
    mock = MagicMock()
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.ilike.return_value = mock
    mock.limit.return_value = mock
    mock.order.return_value = mock
    mock.execute.return_value = Mock(data=[])
    return mock


@pytest.fixture
def mock_openai():
    """Mock do cliente OpenAI"""
    mock = MagicMock()
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "Puerto Madero"
    mock.chat.completions.create.return_value = response
    return mock


@pytest.fixture
def image_manager(mock_supabase, mock_openai):
    """ImageManager com mocks injetados"""
    return ImageManager(
        supabase_client=mock_supabase,
        openai_client=mock_openai
    )


# ============================================================================
# TESTES DE VALIDAÇÃO
# ============================================================================

class TestValidation:
    """Testes da função de validação"""
    
    def test_validate_string_valid(self):
        """Teste com string válida"""
        result = _validate_string_input("Buenos Aires", "city")
        assert result == "Buenos Aires"
    
    def test_validate_string_with_spaces(self):
        """Teste com espaços extras"""
        result = _validate_string_input("  Buenos Aires  ", "city")
        assert result == "Buenos Aires"
    
    def test_validate_string_none(self):
        """Teste com None deve lançar erro"""
        with pytest.raises(ValueError, match="não pode ser None"):
            _validate_string_input(None, "city")
    
    def test_validate_string_empty(self):
        """Teste com string vazia deve lançar erro"""
        with pytest.raises(ValueError, match="não pode ser vazio"):
            _validate_string_input("", "city")
    
    def test_validate_string_wrong_type(self):
        """Teste com tipo errado deve lançar erro"""
        with pytest.raises(TypeError, match="deve ser string"):
            _validate_string_input(123, "city")


# ============================================================================
# TESTES DE NORMALIZAÇÃO
# ============================================================================

class TestNormalize:
    """Testes da função de normalização"""
    
    def test_normalize_remove_stopwords(self):
        """Teste remoção de stopwords"""
        result = _normalize("cityscape foto da cidade de Buenos Aires")
        assert "cityscape" not in result
        assert "buenos aires" in result
    
    def test_normalize_lowercase(self):
        """Teste conversão para minúsculas"""
        result = _normalize("BUENOS AIRES")
        assert result == "buenos aires"
    
    def test_normalize_remove_special_chars(self):
        """Teste remoção de caracteres especiais"""
        result = _normalize("São Paulo!@#$%")
        assert "!" not in result
        assert "@" not in result
    
    def test_normalize_non_string(self):
        """Teste com não-string retorna vazio"""
        result = _normalize(123)
        assert result == ""


# ============================================================================
# TESTES DO IMAGE MANAGER
# ============================================================================

class TestImageManager:
    """Testes da classe ImageManager"""
    
    def test_init_with_clients(self, mock_supabase, mock_openai):
        """Teste inicialização com clientes fornecidos"""
        manager = ImageManager(
            supabase_client=mock_supabase,
            openai_client=mock_openai
        )
        assert manager.db is mock_supabase
        assert manager.ai is mock_openai
    
    def test_buscar_imagem_exato(self, image_manager, mock_supabase):
        """Teste busca com match exato"""
        mock_supabase.execute.return_value.data = [{
            "image_url": "https://example.com/obelisco.jpg",
            "description": "Obelisco de Buenos Aires",
            "landmark": "Obelisco"
        }]
        
        result = image_manager.buscar_imagem("Buenos Aires", "Obelisco")
        
        assert result == "https://example.com/obelisco.jpg"
        mock_supabase.eq.assert_called()
    
    @patch.dict('os.environ', {}, clear=True)
    def test_buscar_imagem_sem_supabase(self):
        """Teste busca sem Supabase disponível"""
        # Força cliente None limpando env vars
        manager = ImageManager(supabase_client=None, openai_client=None)
        
        # Confirma que não inicializou
        assert manager.db is None
        
        result = manager.buscar_imagem("Buenos Aires", "Obelisco")
        assert result is None
    
    def test_buscar_imagem_input_invalido(self, image_manager):
        """Teste busca com input inválido"""
        result = image_manager.buscar_imagem("", "")
        assert result is None
    
    def test_get_hero_image_with_data(self, image_manager, mock_supabase):
        """Teste hero image com dados disponíveis"""
        mock_supabase.execute.return_value.data = [{
            "image_url": "https://example.com/ba.jpg",
            "landmark": "Buenos Aires",
            "quality": 5
        }]
        
        result = image_manager.get_hero_image_for_trip(["Buenos Aires"])
        assert result == "https://example.com/ba.jpg"
    
    def test_get_hero_image_empty_destinations(self, image_manager):
        """Teste hero image sem destinos"""
        result = image_manager.get_hero_image_for_trip([])
        assert result == FALLBACK_URL


# ============================================================================
# TESTES DE NÃO-REPETIÇÃO
# ============================================================================

class TestBuscarImagemParaDia:
    """Testes da função de não-repetição"""
    
    def test_busca_sem_repeticao(self, image_manager, mock_supabase):
        """Teste que imagens não se repetem"""
        # Simular 3 imagens diferentes no banco
        mock_supabase.execute.return_value.data = [
            {"id": "1", "image_url": "url1", "landmark": "L1", "city": "BA", "quality": 5},
            {"id": "2", "image_url": "url2", "landmark": "L2", "city": "BA", "quality": 4},
            {"id": "3", "image_url": "url3", "landmark": "L3", "city": "BA", "quality": 3},
        ]
        
        used_ids = set()
        
        img1 = buscar_imagem_para_dia("Buenos Aires", "L1", used_ids, image_manager)
        img2 = buscar_imagem_para_dia("Buenos Aires", "L2", used_ids, image_manager)
        
        assert img1 is not None
        assert img2 is not None
        assert img1["id"] != img2["id"]
        assert len(used_ids) == 2
    
    def test_busca_input_invalido(self, image_manager):
        """Teste com input inválido"""
        used_ids = set()
        result = buscar_imagem_para_dia("", "", used_ids, image_manager)
        assert result is None
    
    def test_busca_sem_candidatos(self, image_manager, mock_supabase):
        """Teste quando não há imagens disponíveis"""
        mock_supabase.execute.return_value.data = []
        
        used_ids = set()
        result = buscar_imagem_para_dia("Lima", "Plaza", used_ids, image_manager)
        assert result is None


# ============================================================================
# TESTES DE COMPATIBILIDADE
# ============================================================================

class TestCompatibility:
    """Testes das funções legacy"""
    
    @patch('supabase_images._get_manager')
    def test_buscar_imagem_legacy(self, mock_get_manager):
        """Teste função legacy buscar_imagem"""
        mock_manager = Mock()
        mock_manager.buscar_imagem.return_value = "https://example.com/img.jpg"
        mock_get_manager.return_value = mock_manager
        
        result = buscar_imagem("Buenos Aires", "Obelisco")
        
        assert result == "https://example.com/img.jpg"
        mock_manager.buscar_imagem.assert_called_once_with("Buenos Aires", "Obelisco")
