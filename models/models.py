from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from conexao.conexao import *
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

import sqlalchemy as sa

Base = declarative_base()

class CidadeRequest(BaseModel):
    cidade:str = Field(description="Digite a cidade para ser buscada e armazenada as previsões no banco de dados")


class ResponseGlobal(BaseModel):
    status:bool = Field(description="Status da requisicao")
    message:str = Field(description="descricao da requisao")

class ResponsePost(ResponseGlobal):
    data:Optional[dict | None] = Field(description="Dados a serem enviados")

class ClimaResponseAll(BaseModel):
    descricao:str

class DataResponseGetAll(BaseModel):
    cidade:str
    estado:str
    idPrevisao:int
    dataPrevisao:datetime
    temperaturaCelsius:float
    temperaturaCelsiusMaxima:float
    temperaturaCelsiusMinima:float
    pressao:int
    velocidadeVento:float
    visibilidade:int
    clima:List[ClimaResponseAll]

class ResponseGetAll(ResponseGlobal):
    data:Optional[List[DataResponseGetAll]]

class ResponseDelPred(ResponseGlobal):
    data:Optional[str]



class CityRequest(BaseModel):
    id_city: int
    name: str
    latitude: float
    longitude: float
    country: str
    population: int

class WeatherRequest(BaseModel):
    id_weather: int
    main: str
    description: str
    icon: str

class ForecastReques(BaseModel):
    id_city:int
    data_prev: datetime
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    sea_level: int
    grnd_level: int
    humidity: int
    temp_kf: float
    weather: List[WeatherRequest]
    cloud_all: int
    wind_speed: float
    wind_deg: int
    wind_gust: float
    visibility: int
    pop: float
    pod: str
    dt_txt: str
    sunrise: int
    sunset: int
    
class ForecastComplet(BaseModel):
    city: CityRequest
    previsao: List[ForecastReques]



class City(Base):
    __tablename__ = 'cities'

    id_city = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    country = Column(String, nullable=True)
    population = Column(Integer, nullable=True)

    forecasts = relationship('Forecast', back_populates='city')


class Icon(Base):
    __tablename__ = 'icons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)

    weathers = relationship('Weather', back_populates='icon')


class Weather(Base):
    __tablename__ = 'weathers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_weather = Column(Integer, nullable=False)
    main = Column(String, nullable=True)
    description = Column(String, nullable=True)
    id_icon = Column(Integer, ForeignKey('icons.id'))

    icon = relationship('Icon', back_populates='weathers')
    forecasts = relationship('ForecastWeather', back_populates='weather')

    __table_args__ = (UniqueConstraint('id_weather', 'id_icon', name='_weather_icon_uc'),)


class Forecast(Base):
    __tablename__ = 'forecasts'

    id_forecast = Column(Integer, primary_key=True, autoincrement=True)
    id_city = Column(Integer, ForeignKey('cities.id_city'))
    data_prev = Column(DateTime, nullable=False)
    sunrise = Column(DateTime, nullable=True)
    sunset = Column(DateTime, nullable=True)
    offset_utc = Column(Integer, nullable=True)
    temp = Column(Float, nullable=True)
    feels_like = Column(Float, nullable=True)
    temp_min = Column(Float, nullable=True)
    temp_max = Column(Float, nullable=True)
    pressure = Column(Integer, nullable=True)
    sea_level = Column(Integer, nullable=True)
    grnd_level = Column(Integer, nullable=True)
    humidity = Column(Integer, nullable=True)
    temp_kf = Column(Float, nullable=True)
    cloud_all = Column(Integer, nullable=True)
    wind_speed= Column(Float, nullable=True)
    wind_deg= Column(Integer, nullable=True)
    wind_gust= Column(Float, nullable=True)
    visibility= Column(Integer, nullable=True)
    pop= Column(Float, nullable=True)
    pod= Column(String, nullable=True)

    city = relationship('City', back_populates='forecasts')
    weathers = relationship('ForecastWeather', back_populates='forecast')
    __table_args__ = (UniqueConstraint('id_city', 'data_prev', name='_cities_data_uc'),)


class ForecastWeather(Base):
    __tablename__ = 'forecast_weathers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_forecast = Column(Integer, ForeignKey('forecasts.id_forecast'))
    id_weather = Column(Integer, ForeignKey('weathers.id'))

    forecast = relationship('Forecast', back_populates='weathers')
    weather = relationship('Weather', back_populates='forecasts')
