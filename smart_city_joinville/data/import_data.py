import json
import requests
from neo4j import GraphDatabase
from config.config import GOOGLE_MAPS_API_KEY
from .api_fetcher import ApiFetcher

class DataImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.api_fetcher = ApiFetcher()
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def create_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Cidade) REQUIRE c.nome IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Bairro) REQUIRE b.nome IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Rua) REQUIRE r.nome IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sensor) REQUIRE s.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Evento) REQUIRE e.nome IS UNIQUE")
    
    def get_coordinates(self, address):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            return None, None
        except Exception:
            return None, None
    
    def import_static_data(self):
        city_data = [{"nome": "Joinville", "populacao": 600000, "area_km2": 1126.3}]
        bairro_data = [
            {"nome": "América", "populacao": 15000, "area_km2": 5.0, "cidade": "Joinville"},
            {"nome": "Atiradores", "populacao": 12000, "area_km2": 4.0, "cidade": "Joinville"}
        ]
        rua_data = [
            {"nome": "Ottokar Doerffel", "extensao_km": 2.0, "bairro": "América"},
            {"nome": "Dona Francisca", "extensao_km": 3.5, "bairro": "Atiradores"}
        ]
        
        with self.driver.session() as session:
            for city in city_data:
                session.run(
                    "MERGE (c:Cidade {nome: $nome}) "
                    "SET c.populacao = $populacao, c.area_km2 = $area_km2",
                    **city
                )
            for bairro in bairro_data:
                session.run(
                    "MATCH (c:Cidade {nome: $cidade}) "
                    "MERGE (b:Bairro {nome: $nome}) "
                    "SET b.populacao = $populacao, b.area_km2 = $area_km2 "
                    "MERGE (c)-[:CONTÉM]->(b)",
                    **bairro
                )
            for rua in rua_data:
                lat, lng = self.get_coordinates(f"{rua['nome']}, Joinville, SC, Brazil")
                osm_data = self.api_fetcher.fetch_osm_data(rua["nome"])
                if osm_data and osm_data.get("latitude") and osm_data.get("longitude"):
                    lat, lng = osm_data["latitude"], osm_data["longitude"]
                session.run(
                    "MATCH (b:Bairro {nome: $bairro}) "
                    "MERGE (r:Rua {nome: $nome}) "
                    "SET r.extensao_km = $extensao_km, r.latitude = $latitude, r.longitude = $longitude "
                    "MERGE (b)-[:TEM_RUA]->(r)",
                    nome=rua["nome"], extensao_km=rua["extensao_km"], bairro=rua["bairro"],
                    latitude=lat, longitude=lng
                )
    
    def import_api_data(self, rua):
        traffic_data = json.loads(self.api_fetcher.fetch_traffic_data(rua))
        event_data = json.loads(self.api_fetcher.fetch_event_data(rua))
        with self.driver.session() as session:
            session.run(
                "MATCH (r:Rua {nome: $rua}) "
                "SET r.velocidade_media_kmh = $velocidade_media_kmh, r.nivel_trafego = $nivel_trafego",
                **traffic_data
            )
            session.run(
                "MATCH (r:Rua {nome: $rua}) "
                "MERGE (e:Evento {nome: $nome}) "
                "SET e.data = $data, e.tipo = $tipo, e.impacto = $impacto "
                "MERGE (r)-[:TEM_EVENTO]->(e)",
                **event_data
            ) 