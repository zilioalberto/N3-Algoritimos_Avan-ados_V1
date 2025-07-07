import pandas as pd
import json
from collections import defaultdict

def extract_excel_data():
    """Extrai dados do arquivo Excel de Joinville"""
    
    excel_path = "data/581145599-Ruas-de-Joinville.xlsx"
    
    try:
        # Ler o arquivo Excel
        df = pd.read_excel(excel_path)
        
        print("Colunas encontradas no arquivo:")
        print(df.columns.tolist())
        print("\nPrimeiras 10 linhas:")
        print(df.head(10))
        
        # Processar os dados
        return process_excel_data(df)
        
    except Exception as e:
        print(f"Erro ao ler arquivo Excel: {e}")
        return None

def process_excel_data(df):
    """Processa os dados do Excel"""
    
    # A estrutura parece ser: CÓD, NOME, ..., Bairro, ID
    # Vamos identificar as colunas corretas
    
    print("\nAnalisando estrutura do arquivo...")
    
    # Procurar pela linha que contém os cabeçalhos
    header_row = None
    for i, row in df.iterrows():
        if 'CÓD' in str(row.iloc[0]) and 'NOME' in str(row.iloc[1]):
            header_row = i
            break
    
    if header_row is not None:
        print(f"Cabeçalhos encontrados na linha {header_row}")
        # Usar essa linha como cabeçalho
        df_clean = df.iloc[header_row+1:].copy()
        df_clean.columns = df.iloc[header_row]
    else:
        print("Cabeçalhos não encontrados, usando primeira linha")
        df_clean = df.copy()
    
    print("\nColunas após limpeza:")
    print(df_clean.columns.tolist())
    print("\nPrimeiras 5 linhas após limpeza:")
    print(df_clean.head())
    
    # Mapear colunas
    column_mapping = {}
    for i, col in enumerate(df_clean.columns):
        col_str = str(col).strip()
        if 'CÓD' in col_str or 'COD' in col_str:
            column_mapping['codigo'] = i
        elif 'NOME' in col_str:
            column_mapping['nome'] = i
        elif 'Bairro' in col_str or 'BAIRRO' in col_str:
            column_mapping['bairro'] = i
        elif 'ID' in col_str:
            column_mapping['id'] = i
        elif 'LEI' in col_str:
            column_mapping['lei'] = i
        elif 'ANO' in col_str:
            column_mapping['ano'] = i
        elif 'LARGURA' in col_str or 'LARG' in col_str:
            column_mapping['largura'] = i
    
    print("\nMapeamento de colunas:")
    for key, value in column_mapping.items():
        print(f"{key}: coluna {value} ({df_clean.columns[value] if value < len(df_clean.columns) else 'N/A'})")
    
    # Agrupar dados por bairro
    bairros_ruas = defaultdict(list)
    
    for index, row in df_clean.iterrows():
        try:
            # Extrair dados da linha
            codigo = str(row.iloc[column_mapping.get('codigo', 0)]) if 'codigo' in column_mapping else None
            nome_rua = str(row.iloc[column_mapping.get('nome', 1)]) if 'nome' in column_mapping else f"Rua {index}"
            bairro = str(row.iloc[column_mapping.get('bairro', -1)]) if 'bairro' in column_mapping else "Não informado"
            rua_id = row.iloc[column_mapping.get('id', -1)] if 'id' in column_mapping else index
            lei = row.iloc[column_mapping.get('lei', -1)] if 'lei' in column_mapping else None
            ano = row.iloc[column_mapping.get('ano', -1)] if 'ano' in column_mapping else None
            largura = row.iloc[column_mapping.get('largura', -1)] if 'largura' in column_mapping else None
            
            # Limpar dados
            nome_rua = nome_rua.strip()
            bairro = bairro.strip()
            
            if nome_rua and nome_rua != 'nan' and nome_rua != 'None':
                rua_data = {
                    "nome": nome_rua,
                    "codigo": codigo,
                    "largura": largura,
                    "lei": lei,
                    "ano": ano,
                    "id": rua_id
                }
                
                # Usar bairro como chave, ou "Não informado" se não houver
                bairro_key = bairro if bairro and bairro != 'nan' else "Não informado"
                bairros_ruas[bairro_key].append(rua_data)
                
        except Exception as e:
            print(f"Erro ao processar linha {index}: {e}")
            continue
    
    return dict(bairros_ruas)

def save_excel_data(data):
    """Salva os dados extraídos do Excel"""
    if data:
        with open('data/joinville_excel_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\nDados salvos em data/joinville_excel_data.json")
        print(f"Total de bairros encontrados: {len(data)}")
        total_ruas = sum(len(ruas) for ruas in data.values())
        print(f"Total de ruas encontradas: {total_ruas}")
        
        # Mostrar alguns exemplos
        print("\nExemplos de dados extraídos:")
        for bairro, ruas in list(data.items())[:5]:
            print(f"\nBairro: {bairro} ({len(ruas)} ruas)")
            for rua in ruas[:3]:  # Mostrar apenas 3 ruas por bairro
                print(f"  - {rua['nome']} (Código: {rua['codigo']}, ID: {rua['id']})")

if __name__ == "__main__":
    print("Extraindo dados do Excel de Joinville...")
    data = extract_excel_data()
    save_excel_data(data) 