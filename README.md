# Simulado Crypto

API em FastAPI para simular compra e venda de criptoativos em BRL, com carteira, historico de transacoes e autenticacao JWT. Usa CoinGecko para cotacao e MongoDB para persistencia.

## Requisitos
- Python >= 3.10
- MongoDB em execucao

## Configuracao
Crie um arquivo `.env` (opcional) com as variaveis:
- `MONGO_URL` (padrao: `mongodb://localhost:27017`)
- `SECRET_KEY` (obrigatorio para JWT)
- `ALGORITHM` (ex: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (padrao: `50`)

## Instalacao
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

## Execucao
```bash
uvicorn main:app --reload
```

Acesse a documentacao em `/docs`.

## Endpoints principais
- `POST /auth/criar_conta`
- `POST /auth/login`
- `POST /auth/login-form`
- `GET /auth/refresh`
- `GET /carteira/saldo`
- `GET /carteira/cotacao/{moeda}`
- `POST /compra/comprar`
- `POST /venda/vender`
- `GET /historico`

## Arquitetura (Layered)
- Presentation: `app/presentation` (controllers e dependencies do FastAPI)
- Application: `app/application` (camada de orquestracao/servicos)
- Domain: `app/domain` (schemas e modelos)
- Infrastructure: `app/infrastructure` (db, integracoes externas, seguranca)
