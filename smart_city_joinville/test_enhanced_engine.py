#!/usr/bin/env python3
"""
Script de teste para o EnhancedQueryEngine
Testa a integração com a API do Mistral e geração de consultas Cypher
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY
from langchain.enhanced_query_engine import EnhancedQueryEngine

def test_enhanced_engine():
    """Testa o EnhancedQueryEngine com diferentes tipos de perguntas"""
    
    print("🧪 Testando EnhancedQueryEngine com Mistral AI")
    print("=" * 50)
    
    # Verificar se a chave do Mistral está configurada
    if MISTRAL_API_KEY == "your-mistral-api-key":
        print("❌ Erro: Chave da API do Mistral não configurada!")
        print("Configure a variável MISTRAL_API_KEY no arquivo .env")
        return
    
    # Perguntas de teste
    test_questions = [
        "Quantas ruas tem em Joinville?",
        "Quantos bairros tem em Joinville?",
        "Quais são os bairros de Joinville?",
        "Qual bairro tem mais ruas?",
        "Mostre as ruas do bairro Centro"
    ]
    
    try:
        # Inicializar o engine
        engine = EnhancedQueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 Teste {i}: {question}")
            print("-" * 40)
            
            try:
                # Executar consulta
                result = engine.query(question)
                
                # Exibir resultados
                print(f"📝 Resposta LLM: {result['resposta_llm']}")
                print(f"🔍 Consulta Cypher: {result['consulta_cypher']}")
                print(f"📊 Dados encontrados: {len(result['dados_grafo'])} registros")
                
                if result['validacao_externa']:
                    validation = result['validacao_externa']
                    print(f"🌐 Snippet Google: {validation.get('snippet_google', 'N/A')}")
                    print(f"✅ Conferido: {validation.get('conferido', False)}")
                
                print(f"📈 Status: {'✅ Sucesso' if result['resposta_llm'] else '❌ Falha'}")
                
            except Exception as e:
                print(f"❌ Erro no teste {i}: {str(e)}")
        
        engine.close()
        print("\n🎉 Testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar engine: {str(e)}")

if __name__ == "__main__":
    test_enhanced_engine() 