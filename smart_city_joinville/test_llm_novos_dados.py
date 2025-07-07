import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain.query_engine import QueryEngine
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY

def test_llm_novos_dados():
    print("Testando o LLM com os dados atualizados do Neo4j:")
    print("=" * 60)
    query_engine = QueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)

    perguntas = [
        "Quais ruas pertencem ao bairro Espinheiros?",
        "Quais bairros pertencem à cidade de Joinville?",
        "Fale sobre a rua ERVINO MENEGOTTI.",
        "Quantos bairros existem em Joinville?",
        "Liste algumas ruas do bairro América.",
        "Qual o bairro da rua PART HINSCHLING?"
    ]

    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        resposta = query_engine.query(pergunta)
        print(f"Resposta: {resposta}")
        print("-" * 50)

if __name__ == "__main__":
    test_llm_novos_dados() 