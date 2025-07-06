Smart City Joinville Knowledge Graph with Mistral AI and Google Maps
  Um Knowledge Graph no Neo4j para modelar dados reais de Joinville como uma Smart City, integrado com a API da Mistral AI para consultas em linguagem natural, Google Maps JavaScript API para visualização de mapas interativos, e APIs externas para atualização de dados.
Instalação

Instale o Neo4j Desktop ou Aura.
Configure .env com:NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
MISTRAL_API_KEY=your-mistral-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
TRAFFIC_API_KEY=your-traffic-api-key
TRAFFIC_API_URL=https://api.waze.com/traffic


Instale dependências: pip install -r requirements.txt.

Uso

Terminal: Execute python main.py para importar dados e realizar consultas.
Web: Execute python web/app.py para iniciar o servidor Flask e visualizar o mapa em http://localhost:5000.
Testes: python -m unittest tests/test_queries.py.

Fontes de Dados

Joinville Cidade em Dados 2024
Waze for Cities (Smart Mobility)
Perini City Lab (IoT)
Censo 2022 (IBGE)
Google Maps Geocoding API (coordenadas)

Entregáveis

Apresentação: docs/presentation.pdf
Demonstração: docs/demo_video.mp4
