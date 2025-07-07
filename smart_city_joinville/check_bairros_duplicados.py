from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import re

def normalizar_nome(nome):
    # Remove espaços extras, acentos e deixa tudo minúsculo
    nome = nome.strip().lower()
    nome = re.sub(r'\s+', ' ', nome)
    # Remove acentos
    import unicodedata
    nome = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
    return nome

def listar_bairros_duplicados_avancado():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    session = driver.session()
    print("Bairros duplicados (considerando normalização) no banco:")
    print("=" * 60)
    query = '''
    MATCH (b:Bairro)
    RETURN b.nome AS nome
    '''
    result = session.run(query)
    nomes = [record['nome'] for record in result]
    norm_map = {}
    for nome in nomes:
        norm = normalizar_nome(nome)
        if norm not in norm_map:
            norm_map[norm] = []
        norm_map[norm].append(nome)
    encontrou = False
    for norm, lista in norm_map.items():
        if len(lista) > 1:
            encontrou = True
            print(f"Possível duplicidade: {lista}")
    if not encontrou:
        print("Nenhum bairro duplicado (mesmo normalizado) encontrado!")
    session.close()
    driver.close()

if __name__ == "__main__":
    listar_bairros_duplicados_avancado() 