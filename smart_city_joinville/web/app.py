from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_MAPS_API_KEY
from graph.knowledge_graph import KnowledgeGraph
from langchain.query_engine import QueryEngine
from config.config import MISTRAL_API_KEY

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/query', methods=['POST'])
def query():
    question = request.form['question']
    query_engine = QueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)
    response = query_engine.query(question)
    return jsonify({'response': response})

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

if __name__ == '__main__':
    app.run(debug=True) 