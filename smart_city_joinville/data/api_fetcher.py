import requests
    import json
    from mistralai.client import MistralClient
    from config.config import MISTRAL_API_KEY, TOMTOM_API_KEY, OVERPASS_API_URL

    class ApiFetcher:
        def __init__(self):
            self.mistral_client = MistralClient(api_key=MISTRAL_API_KEY)
        
        def fetch_traffic_data(self, rua):
            # Consulta TomTom Traffic Flow API
            try:
                # Coordenadas aproximadas de Joinville para bounding box
                bbox = "-26.35,-48.90,-26.25,-48.80"  # [minLat,minLon,maxLat,maxLon]
                url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={TOMTOM_API_KEY}&point=-26.2978,-48.8492"
                response = requests.get(url)
                response.raise_for_status()
                traffic_data = response.json()
                # Extrair dados relevantes (exemplo simplificado)
                traffic_info = {
                    "rua": rua,
                    "velocidade_media_kmh": traffic_data.get("flowSegmentData", {}).get("currentSpeed", 30),
                    "nivel_trafego": "alto" if traffic_data.get("flowSegmentData", {}).get("currentSpeed", 30) < 20 else "médio"
                }
            except Exception as e:
                print(f"Erro ao acessar TomTom API: {e}")
                traffic_info = {"rua": rua, "velocidade_media_kmh": 30, "nivel_trafego": "médio"}  # Fallback
            prompt = f"""
            Estruture os dados em JSON:
            {traffic_info}
            Formato: {{ "rua": str, "velocidade_media_kmh": float, "nivel_trafego": str }}
            """
            chat_response = self.mistral_client.chat(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return chat_response.choices[0].message.content
        
        def fetch_event_data(self, rua):
            # Consulta TomTom Traffic Incidents API
            try:
                bbox = "-26.35,-48.90,-26.25,-48.80"
                url = f"https://api.tomtom.com/traffic/services/4/incidentDetails?key={TOMTOM_API_KEY}&bbox={bbox}"
                response = requests.get(url)
                response.raise_for_status()
                incident_data = response.json()
                # Extrair primeiro incidente relevante (exemplo simplificado)
                incident = incident_data.get("incidents", [{}])[0]
                event_info = {
                    "nome": f"Incidente_{rua}_{incident.get('id', '2025')}",
                    "data": incident.get("startTime", "2025-07-06"),
                    "tipo": incident.get("type", "Desconhecido"),
                    "impacto": incident.get("description", "Impacto desconhecido"),
                    "rua": rua
                }
            except Exception as e:
                print(f"Erro ao acessar TomTom API: {e}")
                event_info = {
                    "nome": f"Incidente_{rua}_2025",
                    "data": "2025-07-06",
                    "tipo": "Desconhecido",
                    "impacto": "Impacto desconhecido",
                    "rua": rua
                }
            prompt = f"""
            Estruture os dados em JSON:
            {event_info}
            Formato: {{ "nome": str, "data": str, "tipo": str, "impacto": str, "rua": str }}
            """
            chat_response = self.mistral_client.chat(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return chat_response.choices[0].message.content
        
        def fetch_osm_data(self, rua):
            # Consulta Overpass API para coordenadas
            query = f"""
            [out:json];
            area[name="Joinville"]->.searchArea;
            way["highway"]["name"="{rua}"](area.searchArea);
            out center;
            """
            try:
                response = requests.post(OVERPASS_API_URL, data=query)
                response.raise_for_status()
                data = response.json()
                if data["elements"]:
                    element = data["elements"][0]
                    return {
                        "rua": rua,
                        "latitude": element["center"]["lat"],
                        "longitude": element["center"]["lon"]
                    }
                return None
            except Exception:
                return None