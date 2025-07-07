#!/usr/bin/env python3
"""
Script para verificar relacionamentos entre bairros e ruas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from graph.knowledge_graph import KnowledgeGraph

def check_relationships():
    """Verifica os relacionamentos no banco"""
    
    print("🔍 Verificando relacionamentos no banco de dados")
    print("=" * 50)
    
    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # 1. Verificar total de nós
        print("\n📊 Estatísticas gerais:")
        result = kg.query("MATCH (n) RETURN labels(n) AS tipo, count(n) AS total")
        for row in result:
            print(f"  {row['tipo']}: {row['total']} nós")
        
        # 2. Verificar relacionamentos
        print("\n🔗 Relacionamentos:")
        result = kg.query("MATCH ()-[r]->() RETURN type(r) AS tipo, count(r) AS total")
        for row in result:
            print(f"  {row['tipo']}: {row['total']} relacionamentos")
        
        # 3. Verificar se há ruas
        print("\n🛣️ Verificando ruas:")
        result = kg.query("MATCH (r:Rua) RETURN count(r) AS total_ruas")
        total_ruas = result[0]['total_ruas'] if result else 0
        print(f"  Total de ruas: {total_ruas}")
        
        if total_ruas > 0:
            # 4. Verificar algumas ruas
            result = kg.query("MATCH (r:Rua) RETURN r.nome AS nome LIMIT 5")
            print("  Exemplos de ruas:")
            for row in result:
                print(f"    - {row['nome']}")
        
        # 5. Verificar relacionamentos de bairros com ruas
        print("\n🏘️ Relacionamentos Bairro -> Rua:")
        result = kg.query("MATCH (b:Bairro)-[:CONTÉM]->(r:Rua) RETURN count(r) AS total")
        total_rel = result[0]['total'] if result else 0
        print(f"  Total de relacionamentos Bairro->Rua: {total_rel}")
        
        if total_rel == 0:
            print("  ⚠️ Nenhum relacionamento encontrado!")
            print("  Isso explica por que as consultas de ruas não retornam dados.")
            
            # 6. Verificar se há ruas sem relacionamento
            result = kg.query("MATCH (r:Rua) WHERE NOT (r)-[:CONTÉM]-() RETURN count(r) AS total")
            ruas_sem_rel = result[0]['total'] if result else 0
            print(f"  Ruas sem relacionamento: {ruas_sem_rel}")
        
        # 7. Verificar relacionamentos Cidade -> Bairro
        print("\n🏙️ Relacionamentos Cidade -> Bairro:")
        result = kg.query("MATCH (c:Cidade)-[:CONTÉM]->(b:Bairro) RETURN count(b) AS total")
        total_bairros = result[0]['total'] if result else 0
        print(f"  Total de bairros relacionados à cidade: {total_bairros}")
        
        # 8. Verificar bairros sem relacionamento com cidade
        result = kg.query("MATCH (b:Bairro) WHERE NOT (b)-[:CONTÉM]-() RETURN count(b) AS total")
        bairros_sem_rel = result[0]['total'] if result else 0
        print(f"  Bairros sem relacionamento: {bairros_sem_rel}")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    finally:
        kg.close()

if __name__ == "__main__":
    check_relationships() 