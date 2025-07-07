# Smart City Joinville - Integração com Mistral AI

Este projeto agora utiliza a API do Mistral AI para gerar consultas Cypher inteligentes e fornecer respostas mais naturais sobre dados de Joinville.

## 🚀 Configuração da API do Mistral

### 1. Obter Chave da API
1. Acesse [console.mistral.ai](https://console.mistral.ai)
2. Crie uma conta ou faça login
3. Vá para "API Keys" e crie uma nova chave
4. Copie a chave gerada

### 2. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na pasta `smart_city_joinville/` com o seguinte conteúdo:

```env
# Configurações do Neo4j
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=sua_senha_neo4j

# API Keys
MISTRAL_API_KEY=sua_chave_mistral_aqui
GOOGLE_MAPS_API_KEY=sua_chave_google_maps_aqui
```

## 🔧 Funcionalidades do EnhancedQueryEngine

### Geração Inteligente de Consultas Cypher
- O Mistral AI analisa a pergunta em linguagem natural
- Gera consultas Cypher otimizadas baseadas no esquema do banco
- Fallback para consultas básicas em caso de erro

### Respostas Contextualizadas
- Usa os dados do grafo como contexto
- Gera respostas naturais e informativas
- Mantém precisão baseada nos dados reais

### Validação Externa
- Compara respostas com Google Search
- Valida listas de bairros com Wikipedia
- Indica status de conferência

## 📝 Exemplos de Uso

### Perguntas Suportadas
```python
# Contagens
"Quantas ruas tem em Joinville?"
"Quantos bairros tem em Joinville?"

# Listas
"Quais são os bairros de Joinville?"
"Mostre as ruas do bairro Centro"

# Análises
"Qual bairro tem mais ruas?"
"Quais são os bairros mais populosos?"

# Consultas complexas
"Mostre as ruas com maior velocidade média"
"Quais bairros têm ruas com nível de tráfego alto?"
```

### Estrutura de Resposta
```json
{
  "resposta_llm": "Resposta gerada pelo Mistral AI",
  "consulta_cypher": "MATCH (r:Rua) RETURN count(r) AS total_ruas",
  "dados_grafo": [...],
  "validacao_externa": {
    "snippet_google": "Snippet do Google",
    "bairros_wiki": [...],
    "conferido": true
  },
  "conferido": true
}
```

## 🧪 Testando o Sistema

### 1. Teste Básico
```bash
cd smart_city_joinville
python test_enhanced_engine.py
```

### 2. Interface Web
```bash
cd smart_city_joinville
python web/app.py
```
Acesse: http://localhost:5000

### 3. Teste Manual
```python
from langchain.enhanced_query_engine import EnhancedQueryEngine
from config.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY

engine = EnhancedQueryEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MISTRAL_API_KEY)
result = engine.query("Quantas ruas tem em Joinville?")
print(result['resposta_llm'])
engine.close()
```

## 🔍 Interface Web Melhorada

A interface web agora exibe:

1. **🤖 Resposta do Mistral AI**: Resposta natural e contextualizada
2. **🔍 Consulta Cypher Gerada**: Mostra a consulta gerada automaticamente
3. **📊 Dados do Grafo**: Dados brutos retornados pelo Neo4j
4. **🔎 Validação Externa**: Comparação com Google e Wikipedia
5. **🏘️ Comparação de Bairros**: Análise detalhada de diferenças

## ⚠️ Limitações e Considerações

### Custos da API
- A API do Mistral tem custos por token
- Considere implementar cache para consultas repetidas
- Monitore o uso para controlar gastos

### Rate Limiting
- A API tem limites de requisições por minuto
- Implemente delays entre consultas se necessário
- Use fallbacks em caso de erro

### Dependências Externas
- Google Search pode ser bloqueado
- Wikipedia pode estar indisponível
- Implemente tratamento de erros robusto

## 🛠️ Troubleshooting

### Erro: "Chave da API não configurada"
```bash
# Verifique se o arquivo .env existe e tem a chave correta
cat smart_city_joinville/.env
```

### Erro: "Erro ao gerar Cypher com LLM"
- Verifique a conectividade com a API do Mistral
- Confirme se a chave da API é válida
- Verifique se há créditos disponíveis na conta

### Erro: "Erro ao processar consulta"
- Verifique a conexão com o Neo4j
- Confirme se os dados estão carregados
- Verifique os logs para detalhes específicos

## 📈 Próximos Passos

1. **Cache de Consultas**: Implementar cache para consultas frequentes
2. **Fine-tuning**: Treinar o modelo com dados específicos de Joinville
3. **Análise Avançada**: Implementar consultas mais complexas
4. **Integração com APIs**: Conectar com APIs de trânsito em tempo real
5. **Interface Mobile**: Desenvolver aplicativo mobile

## 🤝 Contribuição

Para contribuir com melhorias na integração com Mistral AI:

1. Teste novas funcionalidades
2. Reporte bugs e limitações
3. Sugira melhorias nos prompts
4. Otimize consultas Cypher geradas
5. Implemente novos tipos de validação externa 