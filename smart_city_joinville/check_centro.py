#!/usr/bin/env python3
"""
Script para verificar as ruas do bairro Centro
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from graph.knowledge_graph import KnowledgeGraph

def check_centro():
    """Verifica as ruas do bairro Centro"""
    
    print("🔍 Verificando bairro Centro")
    print("=" * 30)
    
    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # 1. Verificar se o bairro Centro existe
        print("\n🏘️ Verificando bairro Centro:")
        result = kg.query("MATCH (b:Bairro {nome: 'CENTRO'}) RETURN b.nome AS nome")
        if result:
            print(f"✅ Bairro encontrado: {result[0]['nome']}")
        else:
            print("❌ Bairro CENTRO não encontrado!")
            
            # Verificar variações do nome
            result = kg.query("MATCH (b:Bairro) WHERE b.nome CONTAINS 'CENTRO' RETURN b.nome AS nome")
            if result:
                print("🔍 Variações encontradas:")
                for row in result:
                    print(f"  - {row['nome']}")
        
        # 2. Verificar ruas do Centro
        print("\n🛣️ Ruas do Centro:")
        result = kg.query("MATCH (b:Bairro {nome: 'CENTRO'})-[:CONTÉM]->(r:Rua) RETURN count(r) AS total")
        total_ruas = result[0]['total'] if result else 0
        print(f"Total de ruas: {total_ruas}")
        
        if total_ruas > 0:
            # Mostrar algumas ruas
            result = kg.query("MATCH (b:Bairro {nome: 'CENTRO'})-[:CONTÉM]->(r:Rua) RETURN r.nome AS nome LIMIT 10")
            print("Exemplos de ruas:")
            for row in result:
                print(f"  - {row['nome']}")
        
        # 3. Verificar todos os bairros com suas contagens
        print("\n📊 Top 10 bairros com mais ruas:")
        result = kg.query("""
            MATCH (b:Bairro)-[:CONTÉM]->(r:Rua)
            RETURN b.nome AS bairro, count(r) AS total_ruas
            ORDER BY total_ruas DESC
            LIMIT 10
        """)
        for row in result:
            print(f"  {row['bairro']}: {row['total_ruas']} ruas")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    finally:
        kg.close()

if __name__ == "__main__":
    check_centro() 