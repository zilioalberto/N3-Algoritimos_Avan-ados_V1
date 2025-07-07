from mistralai.client import MistralClient
from graph.knowledge_graph import KnowledgeGraph
from config.config import MISTRAL_API_KEY
import requests
from bs4 import BeautifulSoup
import re

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
            resposta_llm = chat_response.choices[0].message.content
            # Buscar resposta no Google
            snippet_google = self._buscar_no_google(question)
            bairros_wiki = []
            # Se a pergunta for sobre bairros, extrair listas e diferenças
            if self._is_bairros_question(question):
                bairros_banco = self._extract_bairros_from_graph(graph_data)
                bairros_google = self._extract_bairros_from_text(snippet_google)
                bairros_wiki = self._buscar_bairros_wikipedia()
                diff_banco = [b for b in bairros_banco if b not in bairros_wiki]
                diff_wiki = [b for b in bairros_wiki if b not in bairros_banco]
                return {
                    'resposta_llm': resposta_llm,
                    'snippet_google': snippet_google,
                    'conferido': len(diff_banco) == 0 and len(diff_wiki) == 0,
                    'bairros_banco': bairros_banco,
                    'bairros_google': bairros_google,
                    'bairros_wiki': bairros_wiki,
                    'so_no_banco': diff_banco,
                    'so_na_wiki': diff_wiki
                }
            # Caso padrão
            conferido = self._comparar_respostas(resposta_llm, snippet_google)
            return {
                'resposta_llm': resposta_llm,
                'snippet_google': snippet_google,
                'conferido': conferido
            }
        except Exception as e:
            return {'resposta_llm': f"Erro ao processar a consulta: {str(e)}", 'snippet_google': '', 'conferido': False}
    
    def _generate_cypher_query(self, question):
        question_lower = question.lower()

        if ("quantas ruas" in question_lower or "número de ruas" in question_lower) and "bairro" not in question_lower:
            return """
            MATCH (r:Rua)
            RETURN count(r) AS total_ruas
            """
        elif ("quantos bairros" in question_lower or "número de bairros" in question_lower) and "cidade" in question_lower:
            return """
            MATCH (b:Bairro)
            RETURN count(b) AS total_bairros
            """
        elif "bairros" in question_lower and "joinville" in question_lower:
            return """
            MATCH (b:Bairro)
            RETURN b.nome AS bairro
            ORDER BY b.nome
            """
        elif "tráfego" in question_lower or "velocidade" in question_lower:
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
            return """
            MATCH (n)
            RETURN labels(n) AS tipo, n.nome AS nome, n.populacao AS populacao
            LIMIT 10
            """
    
    def _format_context(self, graph_data):
        if not graph_data:
            return "Nenhum dado encontrado no grafo."
        # Se a resposta for uma contagem
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

    def _buscar_no_google(self, question):
        try:
            url = f"https://www.google.com/search?q={requests.utils.quote(question)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            # Pega o snippet principal
            snippet = soup.find('div', class_='BNeawe s3v9rd AP7Wnd')
            if snippet:
                return snippet.get_text()
            return ""
        except Exception as e:
            return f"Erro ao buscar no Google: {e}"

    def _comparar_respostas(self, resposta_llm, snippet_google):
        # Comparação simples: se número aparece nas duas respostas
        numeros_llm = re.findall(r'\d+', resposta_llm)
        numeros_google = re.findall(r'\d+', snippet_google)
        if not numeros_llm or not numeros_google:
            return False
        # Se algum número coincide, considera conferido
        for n in numeros_llm:
            if n in numeros_google:
                return True
        return False

    def _is_bairros_question(self, question):
        q = question.lower()
        return ("bairros" in q and "joinville" in q) or ("quais bairros" in q)

    def _extract_bairros_from_graph(self, graph_data):
        bairros = set()
        for item in graph_data:
            if 'bairro' in item:
                bairros.add(item['bairro'].strip().upper())
            elif 'nome' in item:
                bairros.add(item['nome'].strip().upper())
        return sorted(bairros)

    def _extract_bairros_from_text(self, text):
        # Extrai possíveis nomes de bairros de um texto (simples: assume lista separada por vírgula)
        if not text:
            return []
        # Procura listas tipo "Bairros: A, B, C"
        match = re.search(r'(?i)bairros?:?\s*([\w\sÁÉÍÓÚÂÊÎÔÛÃÕÇàáâãéêíóôõúç,-]+)', text)
        if match:
            lista = match.group(1)
            bairros = [b.strip().upper() for b in re.split(r',| e ', lista) if len(b.strip()) > 2]
            return sorted(set(bairros))
        # Se não encontrar, tenta pegar todos os nomes próprios do texto
        return []

    def _buscar_bairros_wikipedia(self):
        try:
            url = "https://pt.wikipedia.org/wiki/Lista_de_bairros_de_Joinville"
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            bairros = []
            # Procura listas em <ul> após <h2> ou <h3> com "Bairros"
            for ul in soup.find_all('ul'):
                if ul.find_previous(['h2', 'h3']) and 'Bairros' in ul.find_previous(['h2', 'h3']).get_text():
                    for li in ul.find_all('li'):
                        nome = li.get_text().strip().upper()
                        if len(nome) > 2:
                            bairros.append(nome)
            # Se não encontrar, tenta pegar todas as listas longas
            if not bairros:
                for ul in soup.find_all('ul'):
                    if len(ul.find_all('li')) > 10:
                        for li in ul.find_all('li'):
                            nome = li.get_text().strip().upper()
                            if len(nome) > 2:
                                bairros.append(nome)
            return sorted(set(bairros))
        except Exception as e:
            return []