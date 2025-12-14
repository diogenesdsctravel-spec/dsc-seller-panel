"""
Anexa imagens únicas aos dias do roteiro.
"""

import logging
from typing import List, Dict, Any, Set
from supabase_images import buscar_imagem_para_dia

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def anexar_imagens_aos_dias(
    dias: List[Dict[str, Any]],
    cidade: str,
    chave_query: str = "landmark",
) -> List[Dict[str, Any]]:
    """
    Anexa imagens únicas a cada dia do roteiro, evitando repetições.
    
    Args:
        dias: Lista de dias do roteiro
        cidade: Nome da cidade da viagem
        chave_query: Campo usado para buscar imagem (default: "landmark")
    
    Returns:
        Lista de dias com campos 'image_url' e 'image_id' adicionados
    """
    used_image_ids: Set[str] = set()
    
    logger.info(f"📸 Buscando fotos para {len(dias)} dias em {cidade}...")
    
    for idx, dia in enumerate(dias, start=1):
        query_text = dia.get(chave_query) or dia.get("titulo") or dia.get("nome") or ""
        query_text = str(query_text).strip()
        
        if not query_text:
            logger.warning(f"  Dia {idx}: sem texto de busca")
            dia["image_url"] = None
            dia["image_id"] = None
            continue
        
        logger.info(f"  Dia {idx}: {query_text}")
        
        imagem = buscar_imagem_para_dia(
            cidade=cidade,
            landmark=query_text,
            used_image_ids=used_image_ids,
        )
        
        if imagem:
            dia["image_url"] = imagem["image_url"]
            dia["image_id"] = imagem["id"]
            logger.info(f"    ✓ {imagem['landmark']}")
        else:
            dia["image_url"] = None
            dia["image_id"] = None
            logger.warning(f"    ✗ Nenhuma foto encontrada")
    
    logger.info(f"✅ {len(used_image_ids)} imagens únicas anexadas aos {len(dias)} dias")
    
    return dias


if __name__ == "__main__":
    # Teste integrado
    from generate_itinerary import generate_itinerary
    
    logger.info("=" * 70)
    logger.info("🧪 TESTE DE INTEGRAÇÃO: ROTEIRO + IMAGENS")
    logger.info("=" * 70)
    
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
    
    # 1. Gerar roteiro
    logger.info("\n📝 ETAPA 1: Gerando roteiro...")
    roteiro = generate_itinerary(test_data)
    
    if not roteiro:
        logger.error("❌ Falha ao gerar roteiro")
        exit(1)
    
    logger.info(f"✅ Roteiro com {len(roteiro)} dias gerado")
    
    # 2. Anexar imagens
    logger.info("\n📸 ETAPA 2: Anexando imagens...")
    roteiro_com_fotos = anexar_imagens_aos_dias(
        dias=roteiro,
        cidade="Buenos Aires",
        chave_query="landmark"
    )
    
    # 3. Verificar resultado
    logger.info("\n" + "=" * 70)
    logger.info("📊 RESULTADO FINAL:")
    logger.info("=" * 70)
    
    image_ids = []
    for dia in roteiro_com_fotos:
        if dia.get("image_id"):
            image_ids.append(dia["image_id"])
            logger.info(
                f"  Dia {dia['dia']}: {dia['landmark']} → "
                f"ID {dia['image_id'][:8]}... ✓"
            )
        else:
            logger.warning(f"  Dia {dia['dia']}: {dia['landmark']} → SEM FOTO ✗")
    
    unique_ids = set(image_ids)
    
    logger.info(f"\n📈 ESTATÍSTICAS:")
    logger.info(f"  Total de dias: {len(roteiro_com_fotos)}")
    logger.info(f"  Dias com foto: {len(image_ids)}")
    logger.info(f"  IDs únicos: {len(unique_ids)}")
    logger.info(f"  Repetições: {len(image_ids) - len(unique_ids)}")
    
    if len(unique_ids) == len(image_ids):
        logger.info("\n✅ SUCESSO! Todas as imagens são únicas!")
    else:
        logger.warning(f"\n⚠️ Há {len(image_ids) - len(unique_ids)} repetições")
    
    logger.info("\n" + "=" * 70)
