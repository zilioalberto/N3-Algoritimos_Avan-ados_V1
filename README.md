# Smart City Joinville - Knowledge Graph com Mistral AI e Google Maps

## Informações do Projeto

**Disciplina:** Algoritmos Avançados  
**Professor:** Glauco  
**Alunos:**
- Alberto Zilio
- Lucas Steffens  
- Lucas D. Gomes
- Roni Pereira

## Descrição do Projeto

Este projeto implementa um Knowledge Graph no Neo4j para modelar dados reais de Joinville como uma Smart City, integrado com tecnologias avançadas de Inteligência Artificial e visualização geográfica:

- **Mistral AI**: Consultas em linguagem natural sobre dados da cidade
- **Google Maps JavaScript API**: Visualização interativa de mapas
- **APIs externas**: Atualização em tempo real de dados de tráfego e mobilidade
- **Neo4j**: Banco de dados de grafos para modelagem de relacionamentos complexos

## Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend Web  │    ┌   Backend API   │    ┌   Neo4j Graph   │
│  (Flask + Maps) │◄──►│  (Python/LLM)   │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Google Maps    │    │   Mistral AI    │    │  External APIs  │
│  JavaScript API │    │   Query Engine  │    │  (Waze, IBGE)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Funcionalidades Principais

### Knowledge Graph
- Modelagem de bairros, ruas e relacionamentos geográficos
- Dados estruturados de Joinville (Cidade em Dados 2024)
- Relacionamentos complexos entre entidades urbanas

### Consultas Inteligentes
- Interface de linguagem natural com Mistral AI
- Consultas semânticas sobre dados da cidade
- Respostas contextualizadas e precisas

### Visualização Interativa
- Mapa interativo com Google Maps
- Visualização de bairros e ruas
- Interface web responsiva

### Dados em Tempo Real
- Integração com Waze for Cities (Smart Mobility)
- Dados de tráfego e mobilidade urbana
- Atualizações automáticas de informações

## Estrutura do Projeto

```
smart_city_joinville/
├── config/                 # Configurações do sistema
├── data/                   # Dados e scripts de importação
│   ├── 581145599-Ruas-de-Joinville.xlsx
│   ├── joinville_structured_data.json
│   └── import_*.py
├── graph/                  # Lógica do Knowledge Graph
│   └── knowledge_graph.py
├── langchain/              # Engine de consultas com IA
│   ├── query_engine.py
│   └── enhanced_query_engine.py
├── web/                    # Interface web
│   ├── app.py
│   ├── static/
│   └── templates/
├── tests/                  # Testes automatizados
├── docs/                   # Documentação
└── main.py                 # Ponto de entrada principal
```

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Neo4j Desktop ou Neo4j Aura
- Contas de API (Mistral AI, Google Maps, Waze)

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd N3-Algoritimos_Avan-ados_V1/smart_city_joinville
```

### 2. Configure as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Neo4j Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# API Keys
MISTRAL_API_KEY=your-mistral-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
TRAFFIC_API_KEY=your-traffic-api-key
TRAFFIC_API_URL=https://api.waze.com/traffic
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Neo4j
- Instale e inicie o Neo4j Desktop ou configure o Neo4j Aura
- Certifique-se de que o banco está acessível com as credenciais configuradas

## Como Usar

### Execução via Terminal
```bash
# Importar dados e executar consultas
python main.py
```

### Interface Web
```bash
# Iniciar servidor Flask
python web/app.py

# Acesse: http://localhost:5000
```

### Executar Testes
```bash
# Testes automatizados
python -m unittest tests/test_queries.py

# Testes específicos
python test_enhanced_engine.py
python test_validacao_oficial.py
```

## Fontes de Dados

### Dados Principais
- **Joinville Cidade em Dados 2024**: Dados oficiais da prefeitura
- **Waze for Cities**: Informações de tráfego e mobilidade
- **Perini City Lab**: Dados de IoT e sensores urbanos
- **Censo 2022 (IBGE)**: Dados demográficos e socioeconômicos

### APIs Externas
- **Google Maps Geocoding API**: Conversão de endereços em coordenadas
- **Google Maps JavaScript API**: Visualização de mapas
- **Mistral AI API**: Processamento de linguagem natural

## Testes e Validação

O projeto inclui uma suíte completa de testes:

- **Testes de Consultas**: Validação das consultas em linguagem natural
- **Testes de Validação Oficial**: Verificação de dados e relacionamentos
- **Testes de Engine Aprimorada**: Validação do motor de consultas
- **Testes de Dados**: Verificação de integridade dos dados

## Documentação

### Arquivos de Documentação
- `docs/presentation.pdf`: Apresentação do projeto
- `docs/demo_video.mp4`: Vídeo demonstrativo
- `README_MISTRAL.md`: Documentação específica do Mistral AI
- `CHANGELOG_MISTRAL.md`: Histórico de mudanças

### Scripts de Validação
- `check_bairros_duplicados.py`: Verificação de duplicatas
- `check_centro.py`: Validação do centro da cidade
- `check_relationships.py`: Verificação de relacionamentos
- `debug_validacao.py`: Debug de validações

## Entregáveis

### Documentação
- README completo com instruções
- Apresentação em PDF
- Vídeo demonstrativo
- Documentação técnica

### Código
- Sistema completo funcional
- Testes automatizados
- Interface web
- Scripts de validação

### Dados
- Knowledge Graph estruturado
- Dados de Joinville integrados
- APIs externas configuradas

## Tecnologias Utilizadas

- **Backend**: Python, Flask, Neo4j
- **Frontend**: HTML, CSS, JavaScript, Google Maps API
- **IA**: Mistral AI, LangChain
- **Dados**: Excel, JSON, APIs REST
- **Testes**: unittest, pytest

## Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `docs/`
2. Execute os scripts de validação
3. Consulte os logs de erro
4. Entre em contato com a equipe do projeto

---

**Desenvolvido para a disciplina de Algoritmos Avançados - 2024**
