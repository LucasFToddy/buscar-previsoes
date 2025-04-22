from sqlalchemy.dialects.postgresql import insert
from conexao.conexao import *
from models.models import *
import requests
import os
import json


def get_predictions_city(cidade:str) -> object | None:
    url = os.getenv("URL_OPEN_WEATHER")
    api_key = os.getenv("API_KEY_OPEN")
    url_get = f"{url}forecast?q={cidade}&appid={api_key}&lang=pt_br&units=metric"
    
    response = requests.get(url=url_get)
    if response.status_code != 200:
        print(f"Erro: {response.text}")
        return None
    response2 = response.json()
    cidade = CityRequest(
    id_city=response2['city']['id']
    ,name=response2['city']['name']
    ,latitude=response2['city']['coord']['lat']
    ,longitude=response2['city']['coord']['lon']
    ,country=response2['city']['country']
    ,population=response2['city']['population']
    )
    lista_prev = []

    for i in response2['list']:
        climas = []
        for c in i['weather']:
            clim = WeatherRequest(
                id_weather=c['id']
                ,main=c['main']
                ,description=c['description']
                ,icon=c['icon']
            )
            climas.append(clim)
        prev = ForecastReques(
            id_city=response2['city']['id']
            ,data_prev=datetime.fromtimestamp(i['dt'])
            ,temp=i['main']['temp']
            ,feels_like=i['main']['feels_like']
            ,temp_min=i['main']['temp_min']
            ,temp_max=i['main']['temp_max']
            ,pressure=i['main']['pressure']
            ,sea_level=i['main']['sea_level']
            ,grnd_level=i['main']['grnd_level']
            ,humidity=i['main']['humidity']
            ,temp_kf=i['main']['temp_kf']
            ,weather=climas
            ,cloud_all=i['clouds']['all']
            ,wind_speed=i['wind']['speed']
            ,wind_deg=i['wind']['deg']
            ,wind_gust=i['wind']['gust']
            ,visibility=i['visibility']
            ,pop=i['pop']
            ,pod=i['sys']['pod']
            ,dt_txt=i['dt_txt']
            ,sunrise=response2['city']['sunrise']
            ,sunset=response2['city']['sunset']
        )
        lista_prev.append(prev)
    forecast_f = ForecastComplet(city=cidade, previsao=lista_prev)
    return forecast_f


def insert_forecast_data(forecast_data: ForecastComplet):
    session = create_session()
    try:
        with session.begin():
            city_data = forecast_data.city
            city = session.get(City, city_data.id_city)
            if not city:
                city = City(**city_data.model_dump())
                session.add(city)

            for prev in forecast_data.previsao:
                existing_forecast = session.execute(
                    select(Forecast).where(
                        Forecast.id_city == city.id_city,
                        Forecast.data_prev == prev.data_prev
                    )
                ).scalar_one_or_none()

                if existing_forecast:
                    forecast = existing_forecast
                    forecast.sunrise = datetime.fromtimestamp(prev.sunrise)
                    forecast.sunset = datetime.fromtimestamp(prev.sunset)
                    forecast.offset_utc = None 
                    forecast.temp = prev.temp
                    forecast.feels_like = prev.feels_like
                    forecast.temp_min = prev.temp_min
                    forecast.temp_max = prev.temp_max
                    forecast.pressure = prev.pressure
                    forecast.sea_level = prev.sea_level
                    forecast.grnd_level = prev.grnd_level
                    forecast.humidity = prev.humidity
                    forecast.temp_kf = prev.temp_kf
                    forecast.cloud_all = prev.cloud_all
                    forecast.pod = prev.pod
                    forecast.wind_speed = prev.wind_speed
                    forecast.wind_deg = prev.wind_deg
                    forecast.wind_gust = prev.wind_gust
                    forecast.visibility = prev.visibility
                    forecast.pop = prev.pop

                    session.query(ForecastWeather).filter_by(
                        id_forecast=forecast.id_forecast
                    ).delete()
                else:
                    forecast = Forecast(
                        id_city=city.id_city,
                        data_prev=prev.data_prev,
                        sunrise=datetime.fromtimestamp(prev.sunrise),
                        sunset=datetime.fromtimestamp(prev.sunset),
                        offset_utc=None,
                        temp=prev.temp,
                        feels_like=prev.feels_like,
                        temp_min=prev.temp_min,
                        temp_max=prev.temp_max,
                        pressure=prev.pressure,
                        sea_level=prev.sea_level,
                        grnd_level=prev.grnd_level,
                        humidity=prev.humidity,
                        temp_kf=prev.temp_kf,
                        cloud_all=prev.cloud_all,
                        pod=prev.pod,
                        wind_speed=prev.wind_speed,
                        wind_deg=prev.wind_deg,
                        wind_gust=prev.wind_gust,
                        visibility=prev.visibility,
                        pop=prev.pop,
                    )
                    session.add(forecast)
                    session.flush()

                for w in prev.weather:
                    icon = session.execute(
                        select(Icon).where(Icon.code == w.icon)
                    ).scalar_one_or_none()
                    if not icon:
                        icon = Icon(code=w.icon)
                        session.add(icon)
                        session.flush()

                    weather = session.execute(
                        select(Weather).where(
                            Weather.id_weather == w.id_weather,
                            Weather.id_icon == icon.id
                        )
                    ).scalar_one_or_none()
                    if not weather:
                        weather = Weather(
                            id_weather=w.id_weather,
                            main=w.main,
                            description=w.description,
                            icon=icon
                        )
                        session.add(weather)
                        session.flush()

                    fw = ForecastWeather(
                        id_forecast=forecast.id_forecast,
                        id_weather=weather.id
                    )
                    session.add(fw)
        return None
    except IntegrityError as e:
        session.rollback()
        return f"Erro de integridade: {str(e)}"
    except Exception as e:
        session.rollback()
        return f"Erro inesperado: {str(e)}"
    finally:
        session.close()


def get_all_predictions() -> tuple[dict | None, int | None]:
    session = create_session()
    result = session.query(
        City.name.label("cidade")
        ,City.country.label("estado")
        ,Forecast.id_forecast.label("idPrevisao")
        ,Forecast.data_prev.label("dataPrevisao")
        ,Forecast.temp.label("temperaturaCelsius")
        ,Weather.description.label("clima")
        ,Forecast.temp_max.label("temperaturaCelsiusMaxima")
        ,Forecast.temp_min.label("temperaturaCelsiusMinima")
        ,Forecast.pressure.label("pressao")
        ,Forecast.wind_speed.label("velocidadeVento")
        ,Forecast.visibility.label("visibilidade")
    ).select_from(City).join(Forecast, Forecast.id_city == City.id_city).join(ForecastWeather, ForecastWeather.id_forecast == Forecast.id_forecast).join(Weather, Weather.id == ForecastWeather.id_weather).all()
    
    result_dicts = []
    for row in result:
        result_dicts.append({
            "cidade": row.cidade,
            "estado": row.estado,
            "idPrevisao": row.idPrevisao,
            "dataPrevisao": row.dataPrevisao,
            "temperaturaCelsius": row.temperaturaCelsius,
            "temperaturaCelsiusMaxima": row.temperaturaCelsiusMaxima,
            "temperaturaCelsiusMinima": row.temperaturaCelsiusMinima,
            "pressao": row.pressao,
            "velocidadeVento": row.velocidadeVento,
            "visibilidade": row.visibilidade,
            "clima": [{"descricao": row.clima}]  # Lista de climas (Weather)
        })
    # Retornando os dados no formato Pydantic
    if len(result_dicts) > 0:
        city_responses = [DataResponseGetAll(**city) for city in result_dicts]
        return (city_responses, len(result))
    return (None, None)


def get_city_date_pred(city:str, data:datetime) -> tuple[dict | None, int | None]:
    session = create_session()
    result = session.query(
        City.name.label("cidade")
        ,City.country.label("estado")
        ,Forecast.id_forecast.label("idPrevisao")
        ,Forecast.data_prev.label("dataPrevisao")
        ,Forecast.temp.label("temperaturaCelsius")
        ,Weather.description.label("clima")
        ,Forecast.temp_max.label("temperaturaCelsiusMaxima")
        ,Forecast.temp_min.label("temperaturaCelsiusMinima")
        ,Forecast.pressure.label("pressao")
        ,Forecast.wind_speed.label("velocidadeVento")
        ,Forecast.visibility.label("visibilidade")
    ).select_from(City).join(
        Forecast, Forecast.id_city == City.id_city
        ).join(
            ForecastWeather, ForecastWeather.id_forecast == Forecast.id_forecast
            ).join(
                Weather, Weather.id == ForecastWeather.id_weather
                ).filter(
                City.name == city,
                func.date(Forecast.data_prev) == data
                ).all()
    
    result_dicts = []
    for row in result:
        result_dicts.append({
            "cidade": row.cidade,
            "estado": row.estado,
            "idPrevisao": row.idPrevisao,
            "dataPrevisao": row.dataPrevisao,
            "temperaturaCelsius": row.temperaturaCelsius,
            "temperaturaCelsiusMaxima": row.temperaturaCelsiusMaxima,
            "temperaturaCelsiusMinima": row.temperaturaCelsiusMinima,
            "pressao": row.pressao,
            "velocidadeVento": row.velocidadeVento,
            "visibilidade": row.visibilidade,
            "clima": [{"descricao": row.clima}]  # Lista de climas (Weather)
        })
    # Retornando os dados no formato Pydantic
    if len(result_dicts) > 0:
        city_responses = [DataResponseGetAll(**city) for city in result_dicts]
        return (city_responses, len(result))
    return (None, None)


def remove_predictions(id_forecast:int) -> str | None:
    session = create_session()
    try:
        previsao = session.query(Forecast).filter(Forecast.id_forecast == id_forecast).first()
        if not previsao:
            return "Previsão não encontrada."

        session.delete(previsao)
        session.commit()
        return None

    except Exception as e:
        session.rollback()
        return f"Erro ao remover previsão: {str(e)}"
    finally:
        session.close()
