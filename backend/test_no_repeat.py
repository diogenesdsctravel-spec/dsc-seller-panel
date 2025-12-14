"""
Teste da funcionalidade de não-repetição de imagens.
"""

import logging
from supabase_images import buscar_imagem_para_dia

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🧪 TESTE DE NÃO-REPETIÇÃO DE IMAGENS")
    logger.info("=" * 70)
    
    # Simular roteiro de 5 dias em Buenos Aires
    used_ids = set()
    
    dias = [
        "Obelisco",
        "Palermo", 
        "La Boca",
        "Puerto Madero",
        "Recoleta"
    ]
    
    logger.info("\n📅 Buscando imagens para roteiro de 5 dias em Buenos Aires:\n")
    
    resultados = []
    for idx, landmark in enumerate(dias, 1):
        logger.info(f"Dia {idx}: {landmark}")
        
        img = buscar_imagem_para_dia(
            cidade="Buenos Aires",
            landmark=landmark,
            used_image_ids=used_ids
        )
        
        if img:
            resultados.append({
                "dia": idx,
                "landmark_busca": landmark,
                "landmark_encontrado": img.get("landmark"),
                "image_id": img.get("id"),
                "url": img.get("image_url", "")[:60] + "..."
            })
            logger.info(f"   ✓ ID: {img['id']} - {img['landmark']}\n")
        else:
            logger.warning(f"   ✗ Nenhuma imagem encontrada\n")
    
    logger.info("=" * 70)
    logger.info("📊 RESUMO:")
    logger.info("=" * 70)
    
    ids_usados = [r["image_id"] for r in resultados]
    ids_unicos = set(ids_usados)
    
    logger.info(f"\nTotal de dias: {len(dias)}")
    logger.info(f"Imagens encontradas: {len(resultados)}")
    logger.info(f"IDs únicos: {len(ids_unicos)}")
    logger.info(f"Repetições: {len(ids_usados) - len(ids_unicos)}")
    
    if len(ids_unicos) == len(resultados):
        logger.info("\n✅ SUCESSO! Todas as imagens são diferentes!")
    else:
        logger.warning("\n⚠️ Há imagens repetidas:")
        for r in resultados:
            count = ids_usados.count(r["image_id"])
            if count > 1:
                logger.warning(f"   ID {r['image_id']} usado {count}x")
    
    logger.info("\n" + "=" * 70)
