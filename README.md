
# Buscador de previsões de tempo

Esse projeto foi realizado para fazer buscar de previsõs de climas. Nela há alguns endpoints, você consegue inserir previsoes a partir de uma API publica e armazenar esses dados no banco de dados postgre que vai funcionar em docker junto com a API





## Documentação da API

#### O endpoint fornece a documentação automática da API gerada pelo Swagger UI, permitindo testar e visualizar os endpoints de forma interativa.
```http
  GET /docs
```

#### Listar todas as previsões armazenadas

```http
  GET /previsao/
```

| Parâmetro   | Tipo       | Descrição                           |
| :---------- | :--------- | :---------------------------------- |
| `api_key` | `string` | **Obrigatório**. A chave da sua API |

#### Buscar previsões filtrando por cidade e data


```http
  GET /previsao/?cidade=São Paulo&data=2025-04-22
```

| Parâmetro   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `cidade`      | `string` | **Obrigatório** |
| `data`      | `datetime` | **Obrigatório** |

#### Buscar previsão do tempo e armazenar no banco

```http
  POST /previsao/
```

| Parâmetro   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `palyload`      | `objecto` | **Obrigatório** |

Payload: { "cidade": "São Paulo" }


#### Excluir uma previsão armazenada

```http
  POST /previsao/{id}
```

| Parâmetro   | Tipo       | Descrição                                   |
| :---------- | :--------- | :------------------------------------------ |
| `id`      | `int` | **id da previsao que se obtem fazendo o get de previsões** |




Devesse criar um arquivo .env para adicionar as variaveis de ambiente que são:

```object

API_KEY_OPEN=sua_api_key
URL_OPEN_WEATHER=https://api.openweathermap.org/data/2.5/

DB_USER=seu_user
DB_PASSWORD=seu_password
DB_HOST=db
DB_PORT=sua_porta
DB_NAME=seu_db
```
