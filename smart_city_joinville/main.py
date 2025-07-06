from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY
  from data.import_data import DataImporter
  from langchain.query_engine import QueryEngine

  def main():
      importer = DataImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
      importer.create_constraints()
      importer.import_static_data()
      importer.import_api_data("Ottokar Doerffel")
      importer.close()
      
      query_engine = QueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)
      questions = [
          "Qual é o tráfego atual na rua Ottokar Doerffel?",
          "Quais eventos recentes ocorreram na rua Ottokar Doerffel?",
          "Quais bairros de Joinville têm população superior a 10 mil habitantes?"
      ]
      for question in questions:
          print(f"\nPergunta: {question}")
          print(f"Resposta: {query_engine.query(question)}")

  if __name__ == "__main__":
      main()