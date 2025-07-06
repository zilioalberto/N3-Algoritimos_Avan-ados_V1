import unittest
from data.import_data import DataImporter
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class TestQueries(unittest.TestCase):
    def setUp(self):
        self.importer = DataImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    def test_import_static_data(self):
        self.importer.create_constraints()
        self.importer.import_static_data()
        with self.importer.driver.session() as session:
            result = session.run("MATCH (c:Cidade {nome: 'Joinville'}) RETURN c")
            self.assertTrue(len([r for r in result]) > 0)
    
    def tearDown(self):
        self.importer.close()

if __name__ == '__main__':
    unittest.main()