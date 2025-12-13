"""
Módulo para gerenciar imagens de destinos no Supabase
"""

from dotenv import load_dotenv
load_dotenv()

import os
from typing import Optional
from supabase import create_client, Client

# Inicializar cliente Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ SUPABASE_URL ou SUPABASE_KEY não configuradas")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase conectado")


def buscar_imagem(city: str, landmark: str) -> Optional[str]:
    """
    Busca imagem curada no Supabase.
    
    Args:
        city: Nome da cidade (ex: "Buenos Aires")
        landmark: Nome do landmark (ex: "Obelisco")
    
    Returns:
        URL da imagem ou None se não encontrar
    """
    if not supabase:
        return None
    
    try:
        result = supabase.table('destination_images')\
            .select('image_url, description')\
            .eq('city', city)\
            .eq('landmark', landmark)\
            .limit(1)\
            .execute()
        
        if result.data and len(result.data) > 0:
            img = result.data[0]
            print(f"💎 [SUPABASE] {city} - {landmark}")
            if img.get('description'):
                print(f"   Desc: {img['description'][:50]}")
            return img['image_url']
        
        return None
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar no Supabase: {e}")
        return None


def salvar_imagem(
    city: str,
    landmark: str,
    image_url: str,
    source: str = 'auto',
    description: str = None
) -> bool:
    """
    Salva imagem no Supabase.
    Se já existir foto do mesmo landmark, cria variação com sufixo numérico.
    
    Args:
        city: Nome da cidade
        landmark: Nome do landmark
        image_url: URL da imagem
        source: Origem ('manual', 'auto', 'unsplash', 'pexels')
        description: Descrição opcional
    
    Returns:
        True se salvou com sucesso
    """
    if not supabase:
        return False
    
    try:
        # Verificar se essa URL JÁ EXISTE (não salvar duplicata da mesma URL)
        existing_url = supabase.table('destination_images')\
            .select('id, landmark')\
            .eq('image_url', image_url)\
            .limit(1)\
            .execute()
        
        if existing_url.data and len(existing_url.data) > 0:
            print(f"⚠️ Esta URL já está cadastrada como: {existing_url.data[0]['landmark']}")
            return False
        
        # Verificar se já existe foto do mesmo city+landmark (variações)
        existing = supabase.table('destination_images')\
            .select('landmark')\
            .eq('city', city)\
            .ilike('landmark', f'{landmark}%')\
            .execute()
        
        # Se já existe, adicionar sufixo numérico
        final_landmark = landmark
        if existing.data and len(existing.data) > 0:
            count = len([x for x in existing.data if x.get('landmark', '').startswith(landmark)])
            if count > 0:
                final_landmark = f"{landmark} {count + 1}"
                print(f"ℹ️ Já existe '{landmark}', salvando como '{final_landmark}'")
        
        data = {
            'city': city,
            'landmark': final_landmark,
            'image_url': image_url,
            'source': source,
            'quality': 5 if source == 'manual' else 4
        }
        
        if description:
            data['description'] = description
        
        # Inserir novo registro (sem upsert)
        supabase.table('destination_images')\
            .insert(data)\
            .execute()
        
        print(f"💾 Salvo no Supabase: {city} - {final_landmark}")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar no Supabase: {e}")
        return False


def listar_todas_imagens():
    """Lista todas as imagens cadastradas (para debug)"""
    if not supabase:
        return []
    
    try:
        result = supabase.table('destination_images')\
            .select('*')\
            .order('city')\
            .execute()
        
        return result.data
        
    except Exception as e:
        print(f"⚠️ Erro ao listar: {e}")
        return []


if __name__ == "__main__":
    # Teste de conexão
    print("=" * 70)
    print("🧪 TESTE DE CONEXÃO SUPABASE")
    print("=" * 70)
    
    # Testar busca (deve retornar None pois ainda não tem dados)
    img = buscar_imagem("Buenos Aires", "Obelisco")
    print(f"\nBusca teste: {img}")
    
    # Testar insert
    print("\n📝 Testando insert...")
    sucesso = salvar_imagem(
        city="Buenos Aires",
        landmark="Obelisco",
        image_url="https://images.unsplash.com/photo-teste",
        source="manual",
        description="Teste de conexão"
    )
    
    if sucesso:
        print("✅ Insert funcionou!")
        
        # Buscar novamente
        print("\n🔍 Buscando novamente...")
        img = buscar_imagem("Buenos Aires", "Obelisco")
        print(f"Resultado: {img}")
    
    print("\n" + "=" * 70)
