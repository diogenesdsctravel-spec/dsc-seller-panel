# 🏗️ Arquitetura Técnica

## Visão Geral

Sistema de 3 camadas para geração de roteiros com imagens únicas:
```
┌─────────────────────────────────────────┐
│      generate_itinerary.py              │
│  (Gera roteiro via OpenAI GPT-4)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  attach_images_to_itinerary.py          │
│  (Orquestra busca de imagens)           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      supabase_images.py                 │
│  (Busca inteligente com IA)             │
└─────────────────────────────────────────┘
```

## Componentes Principais

### 1. ImageManager (supabase_images.py)

**Responsabilidades:**
- Conexão com Supabase
- Matching semântico via OpenAI
- Deduplicação de imagens
- Fallback inteligente

**Métodos Principais:**
- `buscar_imagem(city, landmark)`: Busca normal
- `buscar_imagem_para_dia(city, landmark, used_ids)`: Busca sem repetição
- `encontrar_landmark_semantico(city, landmark)`: Match via IA

**Fluxo de Busca:**
```
buscar_imagem_para_dia
    │
    ├─> 1. Match Exato (city + landmark)
    │   └─> ✓ Achado? → Retorna
    │
    ├─> 2. Matching Semântico (OpenAI)
    │   └─> ✓ Achado? → Retorna
    │
    ├─> 3. City Fallback (qualquer foto da cidade)
    │   └─> ✓ Achado? → Retorna
    │
    └─> 4. None (cidade sem fotos)
```

### 2. ItineraryGenerator (generate_itinerary.py)

**Responsabilidades:**
- Extração de dados da viagem
- Construção de prompts
- Chamada à OpenAI
- Validação de respostas

**Classes:**
```python
TripDataExtractor
├─> extract_main_city()
├─> has_transfer()
└─> get_period()

PromptBuilder
├─> build_itinerary_prompt()
├─> get_system_prompt()
└─> _load_prompt_template()

ResponseProcessor
├─> clean_markdown()
├─> parse_json()
└─> validate_itinerary()

ItineraryGenerator
└─> generate()  # Orquestra tudo
```

### 3. Integração (attach_images_to_itinerary.py)

**Responsabilidades:**
- Loop pelos dias do roteiro
- Chamada ao `buscar_imagem_para_dia`
- Anexa `image_url` e `image_id` a cada dia

## Fluxo End-to-End
```
1. USER INPUT
   ├─> trip_data = { periodo, voos, hoteis, passeios }
   
2. GENERATE ITINERARY
   ├─> TripDataExtractor.extract_main_city()
   ├─> PromptBuilder.build_itinerary_prompt()
   ├─> OpenAI API Call
   ├─> ResponseProcessor.validate_itinerary()
   └─> return dias[]
   
3. ATTACH IMAGES
   ├─> used_image_ids = set()
   ├─> for each dia:
   │   ├─> buscar_imagem_para_dia()
   │   │   ├─> Match Exato
   │   │   ├─> Semantic Match (OpenAI)
   │   │   └─> City Fallback
   │   ├─> dia['image_url'] = img.url
   │   └─> dia['image_id'] = img.id
   └─> return dias_com_fotos[]
   
4. OUTPUT
   └─> Roteiro completo com 0 repetições de imagens
```

## Decisões de Design

### Por que Dependency Injection?
```python
# Permite testes com mocks
manager = ImageManager(
    supabase_client=mock_db,
    openai_client=mock_ai
)

# Facilita configuração customizada
generator = ItineraryGenerator(
    openai_client=custom_client,
    config=custom_config
)
```

### Por que Prompts Externos?

1. **Versionamento**: Git diff nos prompts
2. **A/B Testing**: Trocar arquivo sem redeployar
3. **Colaboração**: Não-devs podem editar
4. **Internacionalização**: Um arquivo por língua

### Por que Matching Semântico?

Usuários não conhecem nomes exatos dos landmarks no banco:
- Usuário: "Ponte da Mulher"
- Banco: "Puerto Madero"
- IA: Faz a conexão ✅

## Padrões Utilizados

### 1. Singleton Pattern
```python
_default_manager: Optional[ImageManager] = None

def _get_manager() -> ImageManager:
    global _default_manager
    if _default_manager is None:
        _default_manager = ImageManager()
    return _default_manager
```

### 2. Strategy Pattern
```python
# Diferentes estratégias de busca
1. Match Exato
2. Semantic Match
3. City Fallback
```

### 3. Template Method Pattern
```python
class ItineraryGenerator:
    def generate(self):
        # Template method
        data = self._extract_data()
        prompt = self._build_prompt()
        response = self._call_api()
        return self._process_response()
```

## Extensibilidade

### Adicionar Nova Cidade
```python
# config.py
LANDMARK_DB.LANDMARKS["NovaCidade"] = [
    "Landmark 1",
    "Landmark 2",
    ...
]
```

### Adicionar Novo Provider de Imagens
```python
class UnsplashImageProvider:
    def search(self, query):
        # Implementar busca no Unsplash
        pass

# Injetar no ImageManager
manager = ImageManager(
    image_provider=UnsplashImageProvider()
)
```

### Customizar Prompts
```bash
# Editar arquivos em prompts/
prompts/itinerary_generation.txt
prompts/system_itinerary.txt
```

## Performance

### Bottlenecks Identificados

1. **OpenAI API Calls**: ~1-2s cada
   - Solução: Batch requests quando possível
   
2. **Supabase Queries**: ~200ms cada
   - Solução: Fetch múltiplos landmarks de uma vez
   
3. **Semantic Matching**: Requer chamada OpenAI
   - Solução: Cache de matches comuns

### Otimizações Futuras

- [ ] Cache de landmarks semânticos
- [ ] Batch OpenAI requests
- [ ] Prefetch de imagens comuns
- [ ] CDN para imagens

## Segurança

### Validação de Inputs
```python
def _validate_string_input(value, param_name):
    if not isinstance(value, str):
        raise TypeError(...)
    if not value.strip():
        raise ValueError(...)
```

### Rate Limiting

- OpenAI: Respeitado via timeouts
- Supabase: Limite de queries por segundo

### Secrets Management
```python
# Nunca committar
OPENAI_API_KEY=...
SUPABASE_KEY=...

# Sempre via environment variables
api_key = os.getenv("OPENAI_API_KEY")
```

## Monitoramento

### Métricas Importantes
```python
# Em produção, adicionar:
- Total de roteiros gerados
- Taxa de sucesso de imagens
- Latência média por operação
- Taxa de matching semântico
- Cache hit rate
```

### Logs Críticos
```python
logger.error()   # Falhas que precisam atenção
logger.warning() # Fallbacks usados
logger.info()    # Operações principais
logger.debug()   # Detalhes internos
```

## Testes

### Estratégia
```
Unit Tests (43 testes)
├─> Funções isoladas
├─> Mocks para externos
└─> Fast (<1s total)

Integration Tests
├─> Conexões reais
├─> End-to-end flow
└─> Slow (~30s)
```

### Coverage
```bash
pytest --cov=. --cov-report=html
# Target: >80% coverage
```

---

**Última atualização:** Dezembro 2024
