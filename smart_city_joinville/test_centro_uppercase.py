#!/usr/bin/env python3
"""
Script para testar consultas do bairro Centro com diferentes variações
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from graph.knowledge_graph import KnowledgeGraph

def test_centro_variations():
    """Testa diferentes variações do nome do bairro Centro"""
    
    print("🔍 Testando variações do bairro Centro")
    print("=" * 40)
    
    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Testar diferentes variações
        variations = ['Centro', 'CENTRO', 'centro', 'Centro ', ' CENTRO']
        
        for variation in variations:
            print(f"\n🔍 Testando: '{variation}'")
            
            # Consulta com variação
            query = f"""
            MATCH (b:Bairro {{nome: '{variation}'}})-[:CONTÉM]->(r:Rua)
            RETURN count(r) AS total_ruas
            """
            result = kg.query(query)
            total = result[0]['total_ruas'] if result else 0
            print(f"  Total de ruas: {total}")
            
            if total > 0:
                # Mostrar algumas ruas
                query_ruas = f"""
                MATCH (b:Bairro {{nome: '{variation}'}})-[:CONTÉM]->(r:Rua)
                RETURN r.nome AS nome LIMIT 5
                """
                ruas = kg.query(query_ruas)
                print("  Exemplos de ruas:")
                for rua in ruas:
                    print(f"    - {rua['nome']}")
        
        # Verificar todos os bairros que contêm "centro"
        print(f"\n🔍 Bairros que contêm 'centro':")
        query = """
        MATCH (b:Bairro)
        WHERE toLower(b.nome) CONTAINS 'centro'
        RETURN b.nome AS nome
        """
        result = kg.query(query)
        for row in result:
            print(f"  - {row['nome']}")
        
        # Verificar bairros que começam com "centro"
        print(f"\n🔍 Bairros que começam com 'centro':")
        query = """
        MATCH (b:Bairro)
        WHERE toLower(b.nome) STARTS WITH 'centro'
        RETURN b.nome AS nome
        """
        result = kg.query(query)
        for row in result:
            print(f"  - {row['nome']}")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    finally:
        kg.close()

if __name__ == "__main__":
    test_centro_variations() 