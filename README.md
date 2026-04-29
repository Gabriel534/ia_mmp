# API Educacional com Busca SQL

API em FastAPI para recomendacao educacional personalizada. A aplicacao recebe a pergunta do estudante, gera consultas `SELECT` seguras com LLM, busca contexto no MySQL e usa esses resultados para montar a resposta final.

## Arquitetura atual

- FastAPI para expor a API
- LangChain Core para orquestrar o pipeline
- Groq como provedor do modelo
- MySQL como fonte de dados dos recursos educacionais
- Docker e Docker Compose para execucao local

## Fluxo da resposta

1. O cliente envia uma pergunta para `POST /ask`.
2. O `RagService` gera ate uma query SQL por categoria:
   - `videos_query`
   - `literature_query`
   - `disciplines_query`
3. O `DatabaseRepository` valida e saneia cada query:
   - permite apenas `SELECT`
   - bloqueia comandos destrutivos
   - restringe o acesso as tabelas `videos`, `literature` e `disciplines`
   - garante `LIMIT`
4. Os resultados retornados pelo MySQL viram contexto para o LLM responder.

## Estrutura de dados esperada

O banco deve conter as tabelas abaixo:

- `videos`
- `literature`
- `disciplines`

O diretorio [`data`](/C:/Users/Usuario/Documents/ia_mmp/data) contem arquivos CSV e scripts SQL de carga, como:

- [`data/insert_videos.sql`](/C:/Users/Usuario/Documents/ia_mmp/data/insert_videos.sql)
- [`data/insert_literature.sql`](/C:/Users/Usuario/Documents/ia_mmp/data/insert_literature.sql)
- [`data/insert_disciplines.sql`](/C:/Users/Usuario/Documents/ia_mmp/data/insert_disciplines.sql)

## Endpoints

### `GET /healthz`

Retorna o status da API.

### `POST /ask`

Recebe a pergunta do estudante e metricas opcionais para personalizar a recomendacao.

Exemplo de payload:

```json
{
  "question": "Como devo estudar calculo?",
  "student_metrics": {
    "risk_score": 72,
    "general_readiness_score": 41,
    "mathematical_foundation_score": 33,
    "autonomy_score": 28
  }
}
```

Exemplo de resposta:

```json
{
  "answer": "..."
}
```

## Variaveis de ambiente

Use o arquivo [`.env.example`](/C:/Users/Usuario/Documents/ia_mmp/.env.example) como base.

```env
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=db_mmp
DB_PORT=3306
DB_USER=app_mmp
DB_PASS=app_mmp
DB_NAME=db_mmp
LLM_MODEL=llama-3.3-70b-versatile
SQL_SEARCH_LIMIT=9
DEBUG=False
LOG_LEVEL=INFO
```

## Execucao

Suba a API com:

```bash
docker compose up --build
```

Observacao: o `docker-compose.yml` usa a rede externa `app_mmp_default`, entao ela precisa existir e o MySQL precisa estar acessivel pelos parametros definidos no `.env`.

## Testes rapidos

```bash
curl http://localhost:8000/healthz
curl.exe -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d "{\"question\":\"Como devo estudar calculo?\"}"
```
