#!/usr/bin/env python3
"""
Script para corrigir relacionamentos entre bairros e ruas
Converte relacionamentos TEM_RUA para CONTÉM
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from graph.knowledge_graph import KnowledgeGraph

def fix_relationships():
    """Corrige os relacionamentos entre bairros e ruas"""
    
    print("🔧 Corrigindo relacionamentos entre bairros e ruas")
    print("=" * 50)
    
    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # 1. Verificar relacionamentos atuais
        print("\n📊 Relacionamentos atuais:")
        result = kg.query("MATCH ()-[r]->() RETURN type(r) AS tipo, count(r) AS total")
        for row in result:
            print(f"  {row['tipo']}: {row['total']} relacionamentos")
        
        # 2. Verificar se há relacionamentos TEM_RUA
        result = kg.query("MATCH ()-[r:TEM_RUA]->() RETURN count(r) AS total")
        tem_rua_count = result[0]['total'] if result else 0
        print(f"\n🛣️ Relacionamentos TEM_RUA: {tem_rua_count}")
        
        if tem_rua_count > 0:
            # 3. Verificar alguns exemplos de TEM_RUA
            print("\n🔍 Exemplos de relacionamentos TEM_RUA:")
            result = kg.query("MATCH (b)-[r:TEM_RUA]->(rua) RETURN b.nome AS bairro, rua.nome AS rua LIMIT 5")
            for row in result:
                print(f"  {row['bairro']} -> {row['rua']}")
            
            # 4. Criar relacionamentos CONTÉM baseados em TEM_RUA
            print("\n🔄 Criando relacionamentos CONTÉM...")
            kg.query("""
                MATCH (b)-[r:TEM_RUA]->(rua)
                CREATE (b)-[:CONTÉM]->(rua)
            """)
            
            # 5. Verificar se foram criados
            result = kg.query("MATCH (b:Bairro)-[:CONTÉM]->(r:Rua) RETURN count(r) AS total")
            contem_count = result[0]['total'] if result else 0
            print(f"✅ Relacionamentos CONTÉM criados: {contem_count}")
            
            # 6. Remover relacionamentos TEM_RUA antigos (opcional)
            print("\n🗑️ Removendo relacionamentos TEM_RUA antigos...")
            kg.query("MATCH ()-[r:TEM_RUA]->() DELETE r")
            
            # 7. Verificar resultado final
            print("\n📊 Relacionamentos finais:")
            result = kg.query("MATCH ()-[r]->() RETURN type(r) AS tipo, count(r) AS total")
            for row in result:
                print(f"  {row['tipo']}: {row['total']} relacionamentos")
            
            # 8. Testar uma consulta
            print("\n🧪 Testando consulta:")
            result = kg.query("MATCH (b:Bairro)-[:CONTÉM]->(r:Rua) RETURN b.nome AS bairro, count(r) AS total_ruas ORDER BY total_ruas DESC LIMIT 5")
            for row in result:
                print(f"  {row['bairro']}: {row['total_ruas']} ruas")
                
        else:
            print("❌ Nenhum relacionamento TEM_RUA encontrado!")
            
            # Verificar se há ruas com propriedade de bairro
            print("\n🔍 Verificando se ruas têm propriedade de bairro...")
            result = kg.query("MATCH (r:Rua) WHERE r.bairro IS NOT NULL RETURN count(r) AS total")
            ruas_com_bairro = result[0]['total'] if result else 0
            print(f"Ruas com propriedade bairro: {ruas_com_bairro}")
            
            if ruas_com_bairro > 0:
                print("🔄 Criando relacionamentos baseados na propriedade bairro...")
                kg.query("""
                    MATCH (r:Rua), (b:Bairro)
                    WHERE r.bairro = b.nome
                    CREATE (b)-[:CONTÉM]->(r)
                """)
                
                result = kg.query("MATCH (b:Bairro)-[:CONTÉM]->(r:Rua) RETURN count(r) AS total")
                contem_count = result[0]['total'] if result else 0
                print(f"✅ Relacionamentos CONTÉM criados: {contem_count}")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    finally:
        kg.close()

if __name__ == "__main__":
    fix_relationships() 