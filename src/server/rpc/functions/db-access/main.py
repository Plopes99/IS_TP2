import psycopg2

connection = None
cursor = None

try:
    connection = psycopg2.connect(user="is",
                                  password="is",
                                  host="is-db",
                                  port="5432",
                                  database="is")

    cursor = connection.cursor()
    cursor.execute("SELECT c.country_name, MAX(d.fatalities) AS max_fatalidades FROM countries c JOIN disasters d ON c.id = d.country_id WHERE d.fatalities IS NOT NULL GROUP BY c.country_name ORDER BY max_fatalidades DESC;")

    print("Desastres com Maior Número de Fatalidades por País:")
    for disaster in cursor:
        print(f" > {disaster[0]}, Nº Mortes: {disaster[1]}")

except (Exception, psycopg2.Error) as error:
    print("Failed to fetch data", error)

finally:
    if connection:
        cursor.close()
        connection.close()