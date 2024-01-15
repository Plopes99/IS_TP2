import sys
import time

import pika
import psycopg2
import xml.etree.ElementTree as ET
from psycopg2 import OperationalError
from datetime import datetime

POLLING_FREQ = int(sys.argv[1]) if len(sys.argv) >= 2 else 60

db_params = {
    'host': 'db-xml',
    'user': 'is',
    'password': 'is',
    'dbname': 'is',
    'port': 5432
}
rabbitMQUser = "is"
rabbitMQPass = "is"
rabbitMQVHost = "is"
rabbitMQAddr = f"amqp://{rabbitMQUser}:{rabbitMQPass}@broker:5672/{rabbitMQVHost}"
rabbitMQPort = 5672

# Configurações da fila
queueName = "migrator_queue"
routingKey = "new_file"
exchangeName = "xml_files"

def connect_to_database():
    """
    Establishes a connection to the PostgreSQL database and returns
    the connection and cursor objects.
    """
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        return conn, cursor
    except psycopg2.Error as e:
        print("Error connecting to the database:", str(e))
        raise

def close_database_connection(conn, cursor):
    """
    Closes the database connection and cursor.
    """
    try:
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print("Error closing the database connection:", str(e))
        raise
def process_country_message(body):
    try:
        country_tree = ET.fromstring(body)
        country_name = country_tree.find('Name').text


    except Exception as e:
        print("Error processing country message:", str(e))

def process_disaster_message(body):
    try:
        disaster_tree = ET.fromstring(body)
        date = disaster_tree.find('Date').text
        aircraft_type = disaster_tree.find('AircraftType').text
        operator = disaster_tree.find('Operator').text
        fatalities = disaster_tree.find('Fatalities').text


        # Faça algo com os detalhes do desastre (por exemplo, inserir no banco de dados)
        print("Processing disaster message:", date, aircraft_type, operator, fatalities)
    except Exception as e:
        print("Error processing disaster message:", str(e))

def process_category_message(body):
    try:
        category_tree = ET.fromstring(body)
        category_name = category_tree.find('Name').text


        # Faça algo com o nome da categoria (por exemplo, inserir no banco de dados)
        print("Processing category message:", category_name)
    except Exception as e:
        print("Error processing category message:", str(e))

def callback(ch, method, properties, body):
    content_type = properties.content_type

    try:
        if content_type == "country":
            process_country_message(body)
        elif content_type == "disaster":
            process_disaster_message(body)
        elif content_type == "category":
            process_category_message(body)
        else:
            print("Unknown content type:", content_type)
    except Exception as e:
        print("Error in callback:", str(e))


def print_psycopg2_exception(ex):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print("\npsycopg2 ERROR:", ex, "on line number:", line_num)
    print("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    print("\nextensions.Diagnostics:", ex.diag)

    # print the pgcode and pgerror exceptions
    print("pgerror:", ex.pgerror)
    print("pgcode:", ex.pgcode, "\n")


if __name__ == "__main__":
    try:
        # Conectar-se ao RabbitMQ
        connection = pika.BlockingConnection(pika.URLParameters(rabbitMQAddr))
        channel = connection.channel()

        # Declarar a fila
        channel.queue_declare(queue='migrator_queue', durable=True)

        # Configurar o consumidor
        channel.basic_consume(queue='migrator_queue', on_message_callback=callback, auto_ack=True)

        # Aguardar por mensagens
        print(' [*] Aguardando por mensagens. Para sair pressione CTRL+C')
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Erro de conexão com RabbitMQ: {e}")
    except KeyboardInterrupt:
        print("Interrompendo o consumidor.")
    finally:
        if connection and connection.is_open:
            # Fechar a conexão ao final
            connection.close()

    db_org = psycopg2.connect(host='db-xml', database='is', user='is', password='is')
    db_dst = psycopg2.connect(host='db-rel', database='is', user='is', password='is')

    while True:

        # Connect to both databases
        db_org = None
        db_dst = None

        try:
            db_org = psycopg2.connect(host='db-xml', database='is', user='is', password='is')
            db_dst = psycopg2.connect(host='db-rel', database='is', user='is', password='is')
        except OperationalError as err:
            print_psycopg2_exception(err)

        if db_dst is None or db_org is None:
            continue

        print("Checking updates...")
        # !TODO: 1- Execute a SELECT query to check for any changes on the table
        # !TODO: 2- Execute a SELECT queries with xpath to retrieve the data we want to store in the relational db
        # !TODO: 3- Execute INSERT queries in the destination db
        # !TODO: 4- Make sure we store somehow in the origin database that certain records were already migrated.
        #          Change the db structure if needed.

        db_org.close()
        db_dst.close()

        time.sleep(POLLING_FREQ)