from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def unificar_bairros():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    session = driver.session()
    print("Unificando bairros duplicados...")
    print("=" * 60)
    grupos = [
        (['FATIMA', 'FÁTIMA'], 'FÁTIMA'),
        (['GLORIA', 'GLÓRIA'], 'GLÓRIA'),
        (['JARDIM PARAISO', 'JARDIM PARAiSO', 'JARDIM PARAÍSO'], 'JARDIM PARAÍSO'),
        (['PETROPOLIS', 'PETRÓPOLIS'], 'PETRÓPOLIS'),
        (['SAO MARCOS', 'SÃO MARCOS'], 'SÃO MARCOS'),
        (['VILA CUBATAO', 'VILA CUBATÃO'], 'VILA CUBATÃO'),
        (['NOVA BRASILIA', 'NOVA BRASÍLIA'], 'NOVA BRASÍLIA'),
    ]
    for variantes, padrao in grupos:
        print(f"\nGrupo: {variantes} -> Mantendo: {padrao}")
        # Garantir que o nó padrão existe
        session.run("MERGE (b:Bairro {nome: $padrao})", padrao=padrao)
        for variante in variantes:
            if variante == padrao:
                continue
            # Redirecionar relações das ruas
            session.run('''
                MATCH (b1:Bairro {nome: $variante})<-[:TEM_RUA]-(r:Rua)
                MATCH (b2:Bairro {nome: $padrao})
                MERGE (b2)<-[:TEM_RUA]-(r)
            ''', variante=variante, padrao=padrao)
            # Redirecionar relação com cidade
            session.run('''
                MATCH (c:Cidade)-[rel:CONTÉM]->(b1:Bairro {nome: $variante})
                MATCH (b2:Bairro {nome: $padrao})
                MERGE (c)-[:CONTÉM]->(b2)
            ''', variante=variante, padrao=padrao)
            # Remover o nó duplicado
            session.run('''
                MATCH (b:Bairro {nome: $variante})
                DETACH DELETE b
            ''', variante=variante)
            print(f"  - {variante} unificado em {padrao}")
    session.close()
    driver.close()
    print("\nUnificação concluída!")

if __name__ == "__main__":
    unificar_bairros() 