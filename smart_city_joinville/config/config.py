import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "your-mistral-api-key")
TRAFFIC_API_KEY = os.getenv("TRAFFIC_API_KEY", "your-traffic-api-key")
TRAFFIC_API_URL = os.getenv("TRAFFIC_API_URL", "https://api.waze.com/traffic")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "your-google-maps-api-key")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "your-tomtom-api-key")
OVERPASS_API_URL = os.getenv("OVERPASS_API_URL", "https://overpass-api.de/api/interpreter")