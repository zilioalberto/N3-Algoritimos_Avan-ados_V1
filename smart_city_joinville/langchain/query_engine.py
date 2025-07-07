from mistralai.client import MistralClient
from graph.knowledge_graph import KnowledgeGraph
from config.config import MISTRAL_API_KEY

class QueryEngine:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, mistral_api_key):
        self.llm = MistralClient(api_key=mistral_api_key)
        self.kg = KnowledgeGraph(neo4j_uri, neo4j_user, neo4j_password)
    
    def query(self, question):
        # Consulta simples no grafo para obter dados relevantes
        cypher_query = self._generate_cypher_query(question)
        try:
            graph_data = self.kg.query(cypher_query)
            # Formatar os dados para o LLM
            context = self._format_context(graph_data)
            # Gerar resposta usando o LLM
            prompt = f"""
            Com base nos dados do grafo de conhecimento sobre Joinville, responda à pergunta.
            
            Dados do grafo:
            {context}
            
            Pergunta: {question}
            
            Responda de forma clara e concisa baseada apenas nos dados fornecidos.
            """
            
            chat_response = self.llm.chat(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            return f"Erro ao processar a consulta: {str(e)}"
    
    def _generate_cypher_query(self, question):
        # Mapeamento simples de perguntas para consultas Cypher
        question_lower = question.lower()
        
        if "tráfego" in question_lower or "velocidade" in question_lower:
            return """
            MATCH (r:Rua)
            WHERE r.velocidade_media_kmh IS NOT NULL
            RETURN r.nome AS rua, r.velocidade_media_kmh AS velocidade, r.nivel_trafego AS nivel
            """
        elif "evento" in question_lower:
            return """
            MATCH (r:Rua)-[:TEM_EVENTO]->(e:Evento)
            RETURN r.nome AS rua, e.nome AS evento, e.tipo AS tipo, e.data AS data
            """
        elif "bairro" in question_lower and "população" in question_lower:
            return """
            MATCH (b:Bairro)
            WHERE b.populacao > 10000
            RETURN b.nome AS bairro, b.populacao AS populacao
            """
        else:
            # Consulta genérica
            return """
            MATCH (n)
            RETURN labels(n) AS tipo, n.nome AS nome, n.populacao AS populacao
            LIMIT 10
            """
    
    def _format_context(self, graph_data):
        if not graph_data:
            return "Nenhum dado encontrado no grafo."
        
        formatted = []
        for item in graph_data:
            formatted.append(str(item))
        
        return "\n".join(formatted)