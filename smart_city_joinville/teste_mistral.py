#!/usr/bin/env python3
"""
Script para testar a API do Mistral com diferentes tipos de perguntas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY
from langchain.enhanced_query_engine import EnhancedQueryEngine
import json

def testar_mistral():
    """Testa a API do Mistral com diferentes cenários"""
    
    print("🧪 Testando API do Mistral")
    print("=" * 40)
    
    # Verificar se a chave do Mistral está configurada
    if MISTRAL_API_KEY == "your-mistral-api-key":
        print("❌ Erro: Chave da API do Mistral não configurada!")
        print("Configure a chave no arquivo config.py")
        return
    
    try:
        # Inicializar o engine
        print("🔌 Conectando ao Neo4j e Mistral...")
        engine = EnhancedQueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)
        print("✅ Conectado com sucesso!")
        
        # Lista de perguntas para testar
        perguntas_teste = [
            {
                "categoria": "Joinville - Bairros",
                "pergunta": "Quais são os bairros de Joinville?",
                "esperado": "Deve retornar lista de bairros"
            },
            {
                "categoria": "Joinville - Contagem",
                "pergunta": "Quantas ruas tem em Joinville?",
                "esperado": "Deve retornar número de ruas"
            },
            {
                "categoria": "Joinville - Específico",
                "pergunta": "Quais ruas existem no bairro Centro de Joinville?",
                "esperado": "Deve retornar ruas do Centro"
            },
            {
                "categoria": "Outra Cidade",
                "pergunta": "Quais são os bairros de Florianópolis?",
                "esperado": "Não deve encontrar dados"
            },
            {
                "categoria": "Pergunta Genérica",
                "pergunta": "Como está o tempo hoje?",
                "esperado": "Não deve encontrar dados relevantes"
            },
            {
                "categoria": "Joinville - Complexa",
                "pergunta": "Quantos bairros tem Joinville e qual o bairro com mais ruas?",
                "esperado": "Deve retornar estatísticas"
            }
        ]
        
        for i, teste in enumerate(perguntas_teste, 1):
            print(f"\n{'='*50}")
            print(f"🧪 Teste {i}: {teste['categoria']}")
            print(f"❓ Pergunta: {teste['pergunta']}")
            print(f"📋 Esperado: {teste['esperado']}")
            print(f"{'='*50}")
            
            try:
                # Executar consulta
                print("🔄 Executando consulta...")
                result = engine.query(teste['pergunta'])
                
                # Exibir resultados
                print(f"\n🤖 Resposta do Mistral:")
                print(f"{result.get('resposta_llm', 'Sem resposta')[:200]}...")
                
                print(f"\n🔍 Consulta Cypher gerada:")
                print(f"{result.get('consulta_cypher', 'N/A')}")
                
                print(f"\n📊 Dados do Grafo:")
                dados_grafo = result.get('dados_grafo', [])
                if dados_grafo:
                    print(f"Encontrados {len(dados_grafo)} registros")
                    if len(dados_grafo) <= 5:
                        for item in dados_grafo:
                            print(f"  - {item}")
                    else:
                        print(f"  - Primeiros 3: {dados_grafo[:3]}")
                        print(f"  - Últimos 2: {dados_grafo[-2:]}")
                else:
                    print("Nenhum dado encontrado")
                
                # Verificar validação
                if result.get('validacao_externa'):
                    validation = result['validacao_externa']
                    print(f"\n🔎 Validação Externa:")
                    print(f"  Conferido: {validation.get('conferido', False)}")
                    if validation.get('bairros_oficiais'):
                        print(f"  Bairros oficiais: {len(validation['bairros_oficiais'])}")
                    if validation.get('bairros_banco'):
                        print(f"  Bairros no banco: {len(validation['bairros_banco'])}")
                
                print(f"\n✅ Teste {i} concluído!")
                
            except Exception as e:
                print(f"❌ Erro no teste {i}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Teste específico da API do Mistral
        print(f"\n{'='*50}")
        print("🧪 Teste Direto da API Mistral")
        print(f"{'='*50}")
        
        try:
            from mistralai.client import MistralClient
            from mistralai.models.chat_completion import ChatMessage
            
            client = MistralClient(api_key=MISTRAL_API_KEY)
            
            messages = [
                ChatMessage(role="user", content="Olá! Você está funcionando? Responda apenas 'Sim, estou funcionando!'")
            ]
            
            chat_response = client.chat(
                model="mistral-large-latest",
                messages=messages
            )
            
            print(f"🤖 Resposta direta do Mistral: {chat_response.choices[0].message.content}")
            print("✅ API do Mistral funcionando perfeitamente!")
            
        except Exception as e:
            print(f"❌ Erro na API direta do Mistral: {str(e)}")
        
        engine.close()
        print(f"\n🎉 Todos os testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_mistral() 