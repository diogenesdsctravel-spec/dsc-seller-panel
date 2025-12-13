"""
Script de curadoria rápida de fotos.
Você só cola a URL, a IA preenche city, landmark e descrição.
"""

from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI
from supabase_images import salvar_imagem

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analisar_foto_com_ia(image_url: str) -> dict:
    """
    IA analisa a URL da foto e extrai:
    - city (cidade)
    - landmark (ponto turístico específico)
    - description (descrição)
    """
    
    print(f"\n🤖 Analisando foto com IA...")
    print(f"   URL: {image_url[:60]}...")
    
    prompt = f"""Analise esta URL de imagem e identifique o destino turístico:

URL: {image_url}

IMPORTANTE:
- CITY = nome da cidade (ex: "Buenos Aires", "Lima", "Paris", "San Carlos de Bariloche")
- LANDMARK = ponto turístico ESPECÍFICO (ex: "Obelisco", "Torre Eiffel", "Cristo Redentor", "Cerro Catedral")
- Se for uma foto genérica da cidade sem landmark específico, use o nome da cidade no landmark também

Exemplos corretos:
- Foto do Obelisco → city: "Buenos Aires", landmark: "Obelisco"
- Foto de La Boca → city: "Buenos Aires", landmark: "La Boca"
- Foto do skyline genérico de BA → city: "Buenos Aires", landmark: "Buenos Aires"
- Foto do Cerro Catedral → city: "San Carlos de Bariloche", landmark: "Cerro Catedral"
- Foto do lago Nahuel Huapi → city: "San Carlos de Bariloche", landmark: "Lago Nahuel Huapi"

Retorne APENAS JSON válido:
{{
  "city": "Nome da Cidade",
  "landmark": "Nome do Landmark Específico",
  "description": "Descrição curta em português (max 100 caracteres)"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Você é especialista em identificar destinos turísticos. Retorne APENAS JSON válido, sem markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        result_text = response.choices[0].message.content.strip()
        
        # Limpar markdown se houver
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])
        
        result = json.loads(result_text)
        
        print(f"✅ IA identificou:")
        print(f"   Cidade: {result.get('city')}")
        print(f"   Landmark: {result.get('landmark')}")
        print(f"   Descrição: {result.get('description')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        return None


def curar_foto_interativa():
    """Modo interativo: você cola URLs, IA preenche o resto"""
    
    print("=" * 70)
    print("📸 CURADORIA RÁPIDA DE FOTOS")
    print("=" * 70)
    print("\nVocê cola a URL da foto do Google Imagens ou Unsplash,")
    print("a IA identifica cidade/landmark automaticamente!")
    print("\n💡 DICA: Use Unsplash para fotos de melhor qualidade:")
    print("   https://unsplash.com/s/photos/obelisco-buenos-aires")
    print("\nDigite 'sair' para encerrar.")
    print("Digite 'listar' para ver fotos já cadastradas.")
    print("=" * 70)
    
    while True:
        print("\n" + "-" * 70)
        comando = input("\n🔗 Cole a URL da foto (ou 'listar'/'sair'): ").strip()
        
        if comando.lower() in ['sair', 'exit', 'quit']:
            print("\n👋 Encerrando curadoria.")
            break
        
        if comando.lower() == 'listar':
            from supabase_images import listar_todas_imagens
            fotos = listar_todas_imagens()
            
            if not fotos:
                print("\n⚠️ Nenhuma foto cadastrada ainda.")
                continue
            
            print("\n📊 FOTOS CADASTRADAS:")
            print("-" * 70)
            for i, foto in enumerate(fotos, 1):
                print(f"\n[{i}] {foto['city']} - {foto['landmark']}")
                print(f"    {foto['description'][:60] if foto.get('description') else 'Sem descrição'}")
                print(f"    Qualidade: {foto['quality']}/5 | Fonte: {foto['source']}")
                print(f"    URL: {foto['image_url'][:60]}...")
            
            continue
        
        if not comando:
            continue
        
        image_url = comando
        
        if not image_url.startswith('http'):
            print("❌ URL inválida. Deve começar com http ou https")
            continue
        
        # IA analisa
        info = analisar_foto_com_ia(image_url)
        
        if not info:
            print("⚠️ Não consegui identificar. Preencha manualmente:")
            city = input("  Cidade: ").strip()
            landmark = input("  Landmark: ").strip()
            description = input("  Descrição: ").strip()
            
            info = {
                "city": city,
                "landmark": landmark,
                "description": description
            }
        
        # Confirmar
        print("\n📝 Dados a salvar:")
        print(f"   Cidade: {info['city']}")
        print(f"   Landmark: {info['landmark']}")
        print(f"   Descrição: {info['description']}")
        print(f"   URL: {image_url[:60]}...")
        
        confirma = input("\n✅ Salvar? (s/n/editar): ").strip().lower()
        
        if confirma in ['editar', 'e']:
            info['city'] = input(f"  Cidade [{info['city']}]: ").strip() or info['city']
            info['landmark'] = input(f"  Landmark [{info['landmark']}]: ").strip() or info['landmark']
            info['description'] = input(f"  Descrição [{info['description']}]: ").strip() or info['description']
            confirma = 's'
        
        if confirma in ['s', 'sim', 'y', 'yes']:
            sucesso = salvar_imagem(
                city=info['city'],
                landmark=info['landmark'],
                image_url=image_url,
                source='manual',
                description=info['description']
            )
            
            if sucesso:
                print("\n🎉 Foto salva com sucesso!")
            else:
                print("\n❌ Erro ao salvar")
        else:
            print("⏭️ Pulando...")
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO FINAL DAS FOTOS CADASTRADAS:")
    print("=" * 70)
    
    from supabase_images import listar_todas_imagens
    fotos = listar_todas_imagens()
    
    if not fotos:
        print("\n⚠️ Nenhuma foto foi cadastrada.")
    else:
        for i, foto in enumerate(fotos, 1):
            print(f"\n[{i}] {foto['city']} - {foto['landmark']}")
            print(f"    {foto['description'][:60] if foto.get('description') else 'Sem descrição'}")
            print(f"    Qualidade: {foto['quality']}/5 | Fonte: {foto['source']}")
    
    print("\n✅ Total: {} foto(s) cadastrada(s)".format(len(fotos)))
    print("=" * 70)


if __name__ == "__main__":
    curar_foto_interativa()
