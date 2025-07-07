from mistralai.client import MistralClient
from graph.knowledge_graph import KnowledgeGraph
from config.config import MISTRAL_API_KEY
import requests
from bs4 import BeautifulSoup
import re
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.bairros_joinville import get_bairros_oficiais, comparar_listas

class EnhancedQueryEngine:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, mistral_api_key):
        self.llm = MistralClient(api_key=mistral_api_key)
        self.kg = KnowledgeGraph(neo4j_uri, neo4j_user, neo4j_password)
        
        # Schema do banco para ajudar o LLM a gerar consultas
        self.db_schema = """
        Esquema do banco Neo4j:
        - Nó (Bairro): {nome, populacao, latitude, longitude}
        - Nó (Rua): {nome, lei, largura, codigo, velocidade_media_kmh, nivel_trafego, latitude, longitude}
        - Nó (Cidade): {nome}
        - Relacionamento: (Bairro)-[:CONTÉM]->(Rua)
        - Relacionamento: (Cidade)-[:CONTÉM]->(Bairro)
        """
    
    def query(self, question):
        try:
            # 1. Gerar consulta Cypher usando o Mistral
            cypher_query = self._generate_cypher_with_llm(question)
            print(f"Consulta Cypher gerada: {cypher_query}")
            
            # 2. Executar consulta no grafo
            graph_data = self.kg.query(cypher_query)
            
            # 3. Formatar contexto para o LLM
            context = self._format_context(graph_data)
            
            # 4. Gerar resposta final usando o Mistral
            final_response = self._generate_final_response(question, context, graph_data)
            
            # 5. Buscar validação externa
            external_validation = self._get_external_validation(question, final_response)
            
            return {
                'resposta_llm': final_response,
                'consulta_cypher': cypher_query,
                'dados_grafo': graph_data,
                'validacao_externa': external_validation,
                'conferido': external_validation.get('conferido', False)
            }
            
        except Exception as e:
            return {
                'resposta_llm': f"Erro ao processar a consulta: {str(e)}",
                'consulta_cypher': '',
                'dados_grafo': [],
                'validacao_externa': {},
                'conferido': False
            }
    
    def _generate_cypher_with_llm(self, question):
        """Usa o Mistral para gerar consultas Cypher mais inteligentes"""
        prompt = f"""
        {self.db_schema}
        
        Com base no esquema acima, gere uma consulta Cypher para responder à pergunta.
        A consulta deve ser válida e eficiente.
        
        IMPORTANTE: Os nomes dos bairros no banco estão em MAIÚSCULO (ex: 'CENTRO', 'BOM RETIRO').
        Use os nomes exatamente como estão no banco.
        
        Pergunta: {question}
        
        Responda apenas com a consulta Cypher, sem explicações adicionais.
        """
        
        try:
            response = self.llm.chat(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            cypher = response.choices[0].message.content.strip()
            
            # Limpar a resposta se vier com markdown
            if cypher.startswith('```cypher'):
                cypher = cypher.replace('```cypher', '').replace('```', '').strip()
            elif cypher.startswith('```'):
                cypher = cypher.replace('```', '').strip()
            
            return cypher
        except Exception as e:
            print(f"Erro ao gerar Cypher com LLM: {e}")
            # Fallback para consultas básicas
            return self._fallback_cypher_query(question)
    
    def _fallback_cypher_query(self, question):
        """Consultas básicas de fallback"""
        question_lower = question.lower()
        
        if "quantas ruas" in question_lower:
            return "MATCH (r:Rua) RETURN count(r) AS total_ruas"
        elif "quantos bairros" in question_lower:
            return "MATCH (b:Bairro) RETURN count(b) AS total_bairros"
        elif "bairros" in question_lower:
            return "MATCH (b:Bairro) RETURN b.nome AS bairro ORDER BY b.nome"
        elif "ruas" in question_lower and "bairro" in question_lower:
            return """
            MATCH (b:Bairro)-[:CONTÉM]->(r:Rua)
            RETURN b.nome AS bairro, count(r) AS total_ruas
            ORDER BY total_ruas DESC
            """
        else:
            return "MATCH (n) RETURN labels(n) AS tipo, n.nome AS nome LIMIT 10"
    
    def _format_context(self, graph_data):
        """Formata os dados do grafo para o contexto do LLM"""
        if not graph_data:
            return "Nenhum dado encontrado no grafo."
        
        if isinstance(graph_data, list) and len(graph_data) == 1:
            item = graph_data[0]
            if "total_ruas" in item:
                return f"Total de ruas em Joinville: {item['total_ruas']}"
            if "total_bairros" in item:
                return f"Total de bairros em Joinville: {item['total_bairros']}"
        
        formatted = []
        for item in graph_data:
            formatted.append(str(item))
        return "\n".join(formatted)
    
    def _generate_final_response(self, question, context, graph_data):
        """Gera resposta final usando o Mistral com contexto dos dados"""
        prompt = f"""
        Você é um assistente especializado em dados sobre a cidade de Joinville, Santa Catarina, Brasil.
        
        Com base nos dados do grafo de conhecimento fornecidos, responda à pergunta de forma clara, 
        precisa e informativa. Use os dados fornecidos como fonte principal de informação.
        
        Dados do grafo:
        {context}
        
        Pergunta: {question}
        
        Instruções:
        1. Responda de forma natural e conversacional
        2. Use apenas os dados fornecidos como fonte
        3. Se não houver dados suficientes, indique isso claramente
        4. Para números, seja preciso e claro
        5. Para listas, organize de forma legível
        """
        
        try:
            response = self.llm.chat(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro ao gerar resposta: {str(e)}"
    
    def _get_external_validation(self, question, llm_response):
        """Busca validação externa (Google, dados oficiais)"""
        try:
            # Buscar no Google
            snippet_google = self._buscar_no_google(question)
            
            # Usar dados oficiais para validação de bairros
            bairros_oficiais = []
            bairros_banco = []
            comparacao_bairros = {}
            if self._is_bairros_question(question):
                bairros_oficiais = get_bairros_oficiais()
                # Comparar dados do banco com dados oficiais
                bairros_banco = self._extract_bairros_from_graph_data()
                if bairros_banco:
                    comparacao_bairros = comparar_listas(bairros_banco, bairros_oficiais)
            
            # Comparar respostas
            conferido = self._comparar_respostas(llm_response, snippet_google, bairros_oficiais)
            
            return {
                'snippet_google': snippet_google,
                'bairros_oficiais': bairros_oficiais,
                'bairros_banco': bairros_banco,
                'comparacao': comparacao_bairros,
                'conferido': conferido
            }
        except Exception as e:
            return {
                'snippet_google': f"Erro na validação: {str(e)}",
                'bairros_oficiais': [],
                'bairros_banco': [],
                'comparacao': {},
                'conferido': False
            }
    
    def _buscar_no_google(self, question):
        """Busca snippet no Google"""
        try:
            url = f"https://www.google.com/search?q={requests.utils.quote(question)}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Tentar diferentes seletores para o snippet
            selectors = [
                'div.BNeawe.s3v9rd.AP7Wnd',
                'div.VwiC3b',
                'div.LwV2X',
                'span.st'
            ]
            
            for selector in selectors:
                snippet = soup.select_one(selector)
                if snippet:
                    return snippet.get_text().strip()
            
            return ""
        except Exception as e:
            return f"Erro ao buscar no Google: {e}"
    
    def _is_bairros_question(self, question):
        """Verifica se a pergunta é sobre bairros"""
        q = question.lower()
        return ("bairros" in q and "joinville" in q) or ("quais bairros" in q)
    
    def _comparar_respostas(self, llm_response, google_snippet, bairros_oficiais=None):
        """Compara respostas do LLM com fontes externas"""
        # Extrair números das respostas
        numeros_llm = re.findall(r'\d+', llm_response)
        numeros_google = re.findall(r'\d+', google_snippet)
        
        # Se há números e eles coincidem
        if numeros_llm and numeros_google:
            for n in numeros_llm:
                if n in numeros_google:
                    return True
        
        # Se é sobre bairros, comparar com dados oficiais (prioridade)
        if bairros_oficiais:
            bairros_llm = self._extract_bairros_from_text(llm_response)
            if bairros_llm:
                matches = sum(1 for b in bairros_llm if b in bairros_oficiais)
                if matches > 0:
                    return True
        
        return False
    
    def _extract_bairros_from_text(self, text):
        """Extrai nomes de bairros de um texto"""
        if not text:
            return []
        
        # Padrões comuns para listas de bairros
        patterns = [
            r'(?i)bairros?:?\s*([\w\sÁÉÍÓÚÂÊÎÔÛÃÕÇàáâãéêíóôõúç,-]+)',
            r'(?i)incluem:?\s*([\w\sÁÉÍÓÚÂÊÎÔÛÃÕÇàáâãéêíóôõúç,-]+)',
            r'(?i)como:?\s*([\w\sÁÉÍÓÚÂÊÎÔÛÃÕÇàáâãéêíóôõúç,-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                lista = match.group(1)
                bairros = [b.strip().upper() for b in re.split(r',| e |, ', lista) if len(b.strip()) > 2]
                return sorted(set(bairros))
        
        return []
    
    def _extract_bairros_from_graph_data(self):
        """Extrai lista de bairros dos dados do grafo"""
        try:
            result = self.kg.query("MATCH (b:Bairro) RETURN b.nome AS nome ORDER BY b.nome")
            return [row['nome'] for row in result]
        except Exception as e:
            print(f"Erro ao extrair bairros do grafo: {e}")
            return []
    
    def close(self):
        """Fecha a conexão com o grafo"""
        self.kg.close() 