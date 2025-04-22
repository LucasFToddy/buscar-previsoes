from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import socket  
import uvicorn

from conexao.conexao import *
from models.models import *
from dados.dados import *
load_dotenv(".env")

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)


description='''
API para buscar e verificar previsões de tempo!
'''

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = conexao()
    print("starting tables...")
    Base.metadata.create_all(bind=engine)
    print("tables started!")
    yield
    print("finalizing tables...")


app = FastAPI(title='Previsões do Tempo',
    description=description,
    version='0.0.1',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'DELETE'],
    allow_headers=['*'],
)


@app.get('/')
def status():
    json = {
        'status': 'ok'
    }
    return json

@app.post('/previsao/', response_model=ResponsePost)
def PostPredictions(payload:CidadeRequest):
    get_prev = get_predictions_city(cidade=payload.cidade)
    if not get_prev:
        return JSONResponse(
            status_code=500,
            content=ResponsePost(
                status=False
                ,message=f"cidade não encontrada: {payload}"
                ,data=None
            ).__dict__
        )
    insert = insert_forecast_data(forecast_data=get_prev)
    if not insert:
        response = ResponsePost(
            status=True
            ,message="Dados cadastrados com sucesso"
            ,data=None
        )
        return response
    response = ResponsePost(
        status=False
        ,message=f"Erro ao cadastrar previsões:{insert}"
        ,data=None
    )
    return response


@app.get('/previsao/', response_model=ResponseGetAll)
def GetPredictions():
    try:
        get_all = get_all_predictions()
        if not get_all[0]:
            response = ResponseGetAll(
                status=True
                ,message=f"Error ao obter dados"
                ,data=None
            )
            return response
        response = ResponseGetAll(
            status=True
            ,message=f"Quantidade de linhas {get_all[1]}"
            ,data=get_all[0]
        )
    except Exception as err:
        return JSONResponse(
                status_code=500,
                content=ResponseGetAll(
                    status=False
                    ,message=f"Erro ao obter dados"
                    ,data=str(err)
                ).__dict__
            )
    
    return response
    

@app.get('/previsao', response_model=ResponseGetAll)
def GetCidadeData(cidade:str, data:datetime):
    try:
        get_all_from_date = get_city_date_pred(city=cidade, data=data)
        if not get_all_from_date[0]:
            response = ResponseGetAll(
                status=True
                ,message=f"Sem dados cadastrados"
                ,data=None
            )
            return response
        response = ResponseGetAll(
            status=True
            ,message=f"Quantidade de linhas {get_all_from_date[1]}"
            ,data=get_all_from_date[0]
        )
    except Exception as err:
        return JSONResponse(
                status_code=500,
                content=ResponseGetAll(
                    status=False
                    ,message=f"Erro ao obter dados"
                    ,data=str(err)
                ).__dict__
            )
    
    return response


@app.delete('/previsao/{id_forecast}', response_model=ResponseDelPred)
def DelPredictions(id_forecast:int):
    try:
        delete_pred = remove_predictions(id_forecast=id_forecast)
        if delete_pred:
            return JSONResponse(
                    status_code=500,
                    content=ResponseDelPred(
                        status=False
                        ,message=f"Erro ao deletar previsao"
                        ,data=delete_pred
                    ).__dict__
                )
        response = ResponseDelPred(
            status=True
            ,message=f"Previsão com ID {id_forecast} removida com sucesso."
            ,data=None
        )
    except Exception as err:
        return JSONResponse(
                status_code=500,
                content=ResponseDelPred(
                    status=False
                    ,message=f"Erro inesperado"
                    ,data=str(err)
                ).__dict__
            )
    return response

if __name__ == "__main__":
    uvicorn.run(app,host=IPAddr, port=8002)
