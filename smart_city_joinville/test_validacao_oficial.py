#!/usr/bin/env python3
"""
Script para testar a validação com dados oficiais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY
from langchain.enhanced_query_engine import EnhancedQueryEngine
from data.bairros_joinville import get_bairros_oficiais, comparar_listas

def test_validacao_oficial():
    """Testa a validação com dados oficiais"""
    
    print("🧪 Testando Validação com Dados Oficiais")
    print("=" * 50)
    
    # Verificar se a chave do Mistral está configurada
    if MISTRAL_API_KEY == "your-mistral-api-key":
        print("❌ Erro: Chave da API do Mistral não configurada!")
        return
    
    try:
        # Inicializar o engine
        engine = EnhancedQueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)
        
        # Testar pergunta sobre bairros
        question = "Quais são os bairros de Joinville?"
        print(f"\n🔍 Testando: {question}")
        
        # Executar consulta
        result = engine.query(question)
        
        # Exibir resultados
        print(f"📝 Resposta LLM: {result['resposta_llm'][:100]}...")
        print(f"🔍 Consulta Cypher: {result['consulta_cypher']}")
        
        # Verificar validação externa
        if result['validacao_externa']:
            validation = result['validacao_externa']
            
            print(f"\n📊 Dados de Validação:")
            print(f"  Bairros no banco: {len(validation.get('bairros_banco', []))}")
            print(f"  Bairros oficiais: {len(validation.get('bairros_oficiais', []))}")
            
            if validation.get('comparacao'):
                comp = validation['comparacao']
                print(f"\n🔍 Comparação Detalhada:")
                print(f"  Total no banco: {comp.get('total_banco', 0)}")
                print(f"  Total oficiais: {comp.get('total_externa', 0)}")
                print(f"  Em comum: {comp.get('total_comum', 0)}")
                
                if comp.get('so_no_banco'):
                    print(f"  Só no banco: {len(comp['so_no_banco'])} bairros")
                    for b in comp['so_no_banco'][:5]:  # Mostrar apenas os primeiros 5
                        print(f"    - {b}")
                
                if comp.get('so_na_externa'):
                    print(f"  Só nos oficiais: {len(comp['so_na_externa'])} bairros")
                    for b in comp['so_na_externa'][:5]:  # Mostrar apenas os primeiros 5
                        print(f"    - {b}")
                
                # Status da validação
                if comp.get('total_comum', 0) > 0:
                    print(f"\n✅ Validação: {comp['total_comum']} bairros conferidos!")
                else:
                    print(f"\n⚠️ Validação: Nenhum bairro em comum encontrado!")
            
            print(f"  Conferido: {validation.get('conferido', False)}")
        
        engine.close()
        print("\n🎉 Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    test_validacao_oficial() 