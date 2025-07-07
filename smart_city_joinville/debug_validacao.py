#!/usr/bin/env python3
"""
Script para debugar a validação e verificar os dados retornados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY
from langchain.enhanced_query_engine import EnhancedQueryEngine
import json

def debug_validacao():
    """Debuga a validação para verificar os dados retornados"""
    
    print("🔍 Debugando Validação")
    print("=" * 30)
    
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
        
        # Exibir estrutura completa da resposta
        print(f"\n📊 Estrutura da resposta:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verificar validação externa especificamente
        if result.get('validacao_externa'):
            validation = result['validacao_externa']
            print(f"\n🔍 Validação Externa:")
            print(f"  snippet_google: {validation.get('snippet_google', 'N/A')}")
            print(f"  bairros_oficiais: {len(validation.get('bairros_oficiais', []))} bairros")
            print(f"  bairros_banco: {len(validation.get('bairros_banco', []))} bairros")
            print(f"  comparacao: {validation.get('comparacao', 'N/A')}")
            print(f"  conferido: {validation.get('conferido', False)}")
            
            # Verificar se há dados oficiais
            if validation.get('bairros_oficiais'):
                print(f"\n📋 Bairros oficiais (primeiros 5):")
                for b in validation['bairros_oficiais'][:5]:
                    print(f"  - {b}")
            
            # Verificar se há dados do banco
            if validation.get('bairros_banco'):
                print(f"\n📋 Bairros do banco (primeiros 5):")
                for b in validation['bairros_banco'][:5]:
                    print(f"  - {b}")
            
            # Verificar comparação
            if validation.get('comparacao'):
                comp = validation['comparacao']
                print(f"\n🔍 Comparação:")
                print(f"  total_banco: {comp.get('total_banco', 0)}")
                print(f"  total_externa: {comp.get('total_externa', 0)}")
                print(f"  total_comum: {comp.get('total_comum', 0)}")
                print(f"  so_no_banco: {comp.get('so_no_banco', [])}")
                print(f"  so_na_externa: {comp.get('so_na_externa', [])}")
        else:
            print("❌ Nenhuma validação externa encontrada!")
        
        engine.close()
        print("\n🎉 Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_validacao() 