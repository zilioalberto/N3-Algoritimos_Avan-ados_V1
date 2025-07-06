from langchain.chains import GraphCypherQAChain
from langchain_community.chat_models import ChatMistralAI
from graph.knowledge_graph import KnowledgeGraph

class QueryEngine:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, mistral_api_key):
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            api_key=mistral_api_key,
            base_url="https://api.mistral.ai/v1"
        )
        self.graph = KnowledgeGraph(neo4j_uri, neo4j_user, neo4j_password).graph
        self.chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True
        )
    
    def query(self, question):
        return self.chain.run(question)