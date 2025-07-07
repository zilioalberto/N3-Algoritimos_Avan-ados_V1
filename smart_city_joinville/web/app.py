from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_MAPS_API_KEY
from graph.knowledge_graph import KnowledgeGraph
from langchain.enhanced_query_engine import EnhancedQueryEngine
from config.config import MISTRAL_API_KEY

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/query', methods=['POST'])
def query():
    question = request.form['question']
    
    # Usar o novo EnhancedQueryEngine
    query_engine = EnhancedQueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)
    
    try:
        response = query_engine.query(question)
        query_engine.close()
        return jsonify({'response': response})
    except Exception as e:
        query_engine.close()
        return jsonify({
            'response': {
                'resposta_llm': f"Erro ao processar consulta: {str(e)}",
                'consulta_cypher': '',
                'dados_grafo': [],
                'validacao_externa': {},
                'conferido': False
            }
        })

@app.route('/map_data')
def map_data():
    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    query = """
    MATCH (r:Rua)
    WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL
    RETURN r.nome AS name, r.latitude AS lat, r.longitude AS lng, 
           r.velocidade_media_kmh AS speed, r.nivel_trafego AS traffic_level
    """
    data = kg.query(query)
    kg.close()
    return jsonify(data)

@app.route('/bairros_data')
def bairros_data():
    """Endpoint para dados dos bairros com coordenadas"""
    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    query = """
    MATCH (b:Bairro)
    WHERE b.latitude IS NOT NULL AND b.longitude IS NOT NULL
    RETURN b.nome AS name, b.latitude AS lat, b.longitude AS lng, 
           b.populacao AS populacao
    ORDER BY b.nome
    """
    data = kg.query(query)
    kg.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True) 