import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_MAPS_API_KEY
import time
import unicodedata

def remover_acentos(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def get_bairro_coordinates(bairro, cidade="Joinville", api_key=GOOGLE_MAPS_API_KEY):
    bairro_sem_acentos = remover_acentos(bairro)
    endereco = f"{bairro_sem_acentos}, {cidade}, SC, Brasil"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(endereco)}&key={api_key}"
    print(f"URL: {url}")
    resp = requests.get(url)
    data = resp.json()
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None

def geocode_all_bairros():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    session = driver.session()
    print("Buscando bairros no banco...")
    result = session.run("MATCH (b:Bairro) RETURN b.nome AS nome ORDER BY b.nome")
    bairros = [record["nome"] for record in result]
    print(f"Total de bairros: {len(bairros)}")
    atualizados = 0
    for bairro in bairros:
        print(f"Buscando coordenadas para: {bairro} ...", end=" ")
        lat, lng = get_bairro_coordinates(bairro)
        if lat and lng:
            session.run("MATCH (b:Bairro {nome: $nome}) SET b.latitude = $lat, b.longitude = $lng", nome=bairro, lat=lat, lng=lng)
            print(f"OK ({lat}, {lng})")
            atualizados += 1
        else:
            print("Não encontrado!")
        time.sleep(0.5)  # Evita limite de requisições da API
    session.close()
    driver.close()
    print(f"\nCoordenadas atualizadas para {atualizados} bairros.")

if __name__ == "__main__":
    geocode_all_bairros() 