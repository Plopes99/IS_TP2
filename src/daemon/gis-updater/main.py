import sys
import time
import os
import pika
import json
import requests


rabbitMQUser = "is"
rabbitMQPass = "is"
rabbitMQVHost = "is"
rabbitMQAddr = f"amqp://{rabbitMQUser}:{rabbitMQPass}@broker:5672/{rabbitMQVHost}"
rabbitMQPort = 5672

class GeoLocation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class DisasterMessage:
    def __init__(self,id, date, aircraft_type, operator, fatalities, geo=None):
        self.id = id
        self.date = date
        self.aircraft_type = aircraft_type
        self.operator = operator
        self.fatalities = fatalities
        self.geo = geo

def process_geo_message(body):
    try:
        data = json.loads(body)
        id_value = data.get('id')
        country_id_value = data.get('countryID')
        date = data.get('date')
        aircraftType = data.get('aircraftType')
        operator = data.get('operator')
        fatalities = data.get('fatalities')

        disaster_message = DisasterMessage(
            id=id_value,
            date=date,
            aircraft_type=aircraftType,
            operator=operator,
            fatalities=fatalities,
        )

        country_name= get_country_name_by_id(country_id_value)
        geo = obter_coordenadas_nominatim(country_name)
        update_disaster(disaster_message, geo, country_id_value)
        
    except Exception as e:
        print("Error processing message:", str(e))


def obter_coordenadas_nominatim(nome_pais):
    url = f"https://nominatim.openstreetmap.org/search?country={nome_pais}&format=json"

    response = requests.get(url)
    response.raise_for_status()

    resultados = response.json()

    if not resultados:
        raise ValueError(f"Nenhum resultado encontrado para o país: {nome_pais}")

    # Obtém as coordenadas do primeiro resultado
    latitude = float(resultados[0]["lat"])
    longitude = float(resultados[0]["lon"])
    print(latitude,longitude)

    return GeoLocation(latitude, longitude)

def get_country_name_by_id(country_id):
    url = f"http://api-entities:8080/countries/{country_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()  
        country_data = response.json()
        country_name = country_data.get("countryName")

        if country_name:
            return country_name
        else:
            print("Nome do país não encontrado na resposta.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição HTTP: {e}")
        return None
    

def update_disaster(disaster_message, geo, countryId):
    url = f"http://api-entities:8080/disasters/{disaster_message.id}"


    update_data = {
        "date": disaster_message.date,
        "aircraftType": disaster_message.aircraft_type,
        "operator": disaster_message.operator,
        "fatalities": disaster_message.fatalities,
        "countryId": countryId,
        "geo": {"type": "Point", "coordinates": [geo.latitude, geo.longitude]}
    }

    try:
        response = requests.put(url, json=update_data)
        response.raise_for_status()  

        if response.status_code == 200:
            print(f"Atualização bem-sucedida para a entidade {disaster_message.id}")
        else:
            print(f"Atualização falhou. Status Code: {response.status_code}, Mensagem: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição HTTP: {e}")

def callback(ch, method, properties, body):
    content_type = properties.content_type
    try:
        if content_type == "update-gis":
            process_geo_message(body)
        else:
            pass
    except Exception as e:
        print("Error in callback:", str(e))


if __name__ == "__main__":

    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitMQAddr))
        channel = connection.channel()

        channel.basic_consume(queue='fila_update-gis', on_message_callback=callback, auto_ack=True)

        print(' [*] Aguardando por mensagens. Para sair pressione CTRL+C')
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Erro de conexão com RabbitMQ: {e}")
    except KeyboardInterrupt:
        print("Interrompendo o consumidor.")
    finally:
        if connection and connection.is_open:
            # Fecha a conexão
            connection.close()

    

