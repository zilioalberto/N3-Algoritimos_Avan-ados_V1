import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def importar_ruas_bairros_fixed():
    excel_path = "data/581145599-Ruas-de-Joinville.xlsx"
    
    # Ler o Excel com cabeçalho na linha 1 (índice 0)
    df = pd.read_excel(excel_path, header=1)
    
    print("Colunas detectadas:")
    print(df.columns.tolist())
    print("\nPrimeiras 5 linhas:")
    print(df.head())
    
    # Mapear colunas corretamente
    col_map = {
        'CÓD': 'codigo',
        'NOME': 'nome', 
        'LARGURA': 'largura',
        'LEI': 'lei',
        'ANO': 'ano',
        'INDICE': 'indice',
        'Bairro': 'bairro',
        'ID': 'id'
    }
    
    # Renomear colunas
    df = df.rename(columns=col_map)
    
    print("\nColunas após renomeação:")
    print(df.columns.tolist())
    
    # Conectar ao Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    success_count = 0
    error_count = 0
    
    with driver.session() as session:
        # Garantir constraints
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Bairro) REQUIRE b.nome IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Rua) REQUIRE r.codigo IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Cidade) REQUIRE c.nome IS UNIQUE")
        
        # Limpar dados existentes
        session.run("MATCH (n) DETACH DELETE n")
        
        # Criar nó da cidade Joinville
        session.run("MERGE (c:Cidade {nome: 'Joinville'}) SET c.populacao = 600000, c.area_km2 = 1126.3")
        
        bairros_criados = set()
        
        for idx, row in df.iterrows():
            try:
                # Validar campos essenciais
                codigo = str(row['codigo']).strip() if pd.notna(row['codigo']) else None
                nome = str(row['nome']).strip() if pd.notna(row['nome']) else None
                bairro = str(row['bairro']).strip() if pd.notna(row['bairro']) else None
                
                if not codigo or not nome or codigo == 'nan' or nome == 'nan':
                    continue
                
                # Se não há bairro, usar "Não informado"
                if not bairro or bairro == 'nan':
                    bairro = "Não informado"
                
                # Outros campos
                largura = row['largura'] if pd.notna(row['largura']) else None
                lei = row['lei'] if pd.notna(row['lei']) else None
                ano = row['ano'] if pd.notna(row['ano']) else None
                indice = row['indice'] if pd.notna(row['indice']) else None
                id_val = row['id'] if pd.notna(row['id']) else None
                
                # Criar/garantir bairro
                session.run(
                    "MERGE (b:Bairro {nome: $bairro})",
                    bairro=bairro
                )
                
                # Relacionar bairro à cidade Joinville (apenas uma vez por bairro)
                if bairro not in bairros_criados:
                    session.run(
                        "MATCH (c:Cidade {nome: 'Joinville'}), (b:Bairro {nome: $bairro}) "
                        "MERGE (c)-[:CONTÉM]->(b)",
                        bairro=bairro
                    )
                    bairros_criados.add(bairro)
                
                # Criar/garantir rua, agora com o campo 'name' igual ao 'nome'
                session.run(
                    "MERGE (r:Rua {codigo: $codigo}) "
                    "SET r.nome = $nome, r.name = $nome, r.largura = $largura, r.lei = $lei, "
                    "r.ano = $ano, r.indice = $indice, r.id = $id_val",
                    codigo=codigo, nome=nome, largura=largura, lei=lei, 
                    ano=ano, indice=indice, id_val=id_val
                )
                
                # Relacionar rua ao bairro
                session.run(
                    "MATCH (b:Bairro {nome: $bairro}), (r:Rua {codigo: $codigo}) "
                    "MERGE (b)-[:TEM_RUA]->(r)",
                    bairro=bairro, codigo=codigo
                )
                
                success_count += 1
                
                if success_count % 100 == 0:
                    print(f"Importadas {success_count} ruas...")
                    
            except Exception as e:
                error_count += 1
                print(f"Erro na linha {idx}: {e}")
                if error_count > 10:  # Limitar erros exibidos
                    break
    
    driver.close()
    print(f"\nImportação concluída!")
    print(f"Total de ruas importadas: {success_count}")
    print(f"Total de erros: {error_count}")

if __name__ == "__main__":
    importar_ruas_bairros_fixed() 