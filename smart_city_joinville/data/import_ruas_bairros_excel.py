import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def importar_ruas_bairros():
    excel_path = "data/581145599-Ruas-de-Joinville.xlsx"
    df = pd.read_excel(excel_path, header=None)

    # Encontrar a linha de cabeçalho correta
    header_row = None
    for i, row in df.iterrows():
        if 'CÓD' in str(row.iloc[0]) and 'NOME' in str(row.iloc[1]):
            header_row = i
            break
    if header_row is not None:
        header = [str(col).strip() for col in df.iloc[header_row]]
        df = df.iloc[header_row+1:].copy()
        df.columns = header
    else:
        df.columns = [str(col).strip() for col in df.columns]

    print("Colunas após processamento:")
    print(df.columns.tolist())
    print("Primeiras 5 linhas após processamento:")
    print(df.head())

    # Renomear colunas para facilitar
    col_map = {}
    for col in df.columns:
        col_lower = str(col).lower()
        if 'cód' in col_lower or 'cod' in col_lower:
            col_map['codigo'] = col
        elif 'nome' in col_lower:
            col_map['nome'] = col
        elif 'largura' in col_lower or 'larg' in col_lower:
            col_map['largura'] = col
        elif 'lei' in col_lower:
            col_map['lei'] = col
        elif 'ano' in col_lower:
            col_map['ano'] = col
        elif 'id' in col_lower or 'índice' in col_lower or 'indice' in col_lower:
            col_map['indice'] = col
        elif 'bairro' in col_lower:
            col_map['bairro'] = col

    print("\nMapeamento de colunas detectado:")
    for k, v in col_map.items():
        print(f"{k}: {v}")

    # Conectar ao Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    success_count = 0
    with driver.session() as session:
        # Garantir constraints
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Bairro) REQUIRE b.nome IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Rua) REQUIRE r.codigo IS UNIQUE")

        for _, row in df.iterrows():
            try:
                # Validar campos essenciais
                if not all(k in col_map for k in ['codigo', 'nome', 'bairro']):
                    continue
                codigo = str(row[col_map['codigo']]).strip()
                nome = str(row[col_map['nome']]).strip()
                bairro = str(row[col_map['bairro']]).strip()
                if not codigo or not nome or not bairro or codigo.lower() == 'nan' or nome.lower() == 'nan' or bairro.lower() == 'nan':
                    continue
                largura = row[col_map['largura']] if 'largura' in col_map else None
                lei = row[col_map['lei']] if 'lei' in col_map else None
                ano = row[col_map['ano']] if 'ano' in col_map else None
                indice = row[col_map['indice']] if 'indice' in col_map else None

                # Criar/garantir bairro
                session.run(
                    "MERGE (b:Bairro {nome: $bairro})",
                    bairro=bairro
                )
                # Criar/garantir rua
                session.run(
                    "MERGE (r:Rua {codigo: $codigo}) "
                    "SET r.nome = $nome, r.largura = $largura, r.lei = $lei, r.ano = $ano, r.indice = $indice",
                    codigo=codigo, nome=nome, largura=largura, lei=lei, ano=ano, indice=indice
                )
                # Relacionar rua ao bairro
                session.run(
                    "MATCH (b:Bairro {nome: $bairro}), (r:Rua {codigo: $codigo}) "
                    "MERGE (b)-[:TEM_RUA]->(r)",
                    bairro=bairro, codigo=codigo
                )
                success_count += 1
            except Exception as e:
                print(f"Erro ao importar linha: {e}")
    driver.close()
    print(f"Importação concluída! Total de ruas importadas: {success_count}")

if __name__ == "__main__":
    importar_ruas_bairros() 