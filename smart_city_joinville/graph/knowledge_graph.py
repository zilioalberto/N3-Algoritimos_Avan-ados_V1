from neo4j import GraphDatabase
from langchain.graphs import Neo4jGraph

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.graph = Neo4jGraph(url=uri, username=user, password=password)
    
    def close(self):
        self.driver.close()
    
    def query(self, cypher_query):
        with self.driver.session() as session:
            result = session.run(cypher_query)
            return [record.data() for record in result]