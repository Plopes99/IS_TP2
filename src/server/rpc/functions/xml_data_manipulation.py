import psycopg2


def connect_to_database():
    try:
        conn = psycopg2.connect(user="is",
                                password="is",
                                host="is-db",
                                port="5432",
                                database="is")

        return conn
    except (Exception, psycopg2.Error) as error:
        raise RuntimeError(f"Failed to connect to the database: {error}")


def execute_query(query):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except (Exception, psycopg2.Error) as error:
        raise RuntimeError(f"Failed to execute query: {error}")


def get_disaster_by_year():
    query = """
    SELECT
    extract_valid_year(disaster_date) AS year,
    COUNT(*) AS num_disasters
    FROM (
    SELECT unnest(xpath('/airplane_disasters/category/country/disaster/date/@text', xml)::text[]) AS disaster_date
    FROM public.imported_documents
    ) AS disaster_dates
    WHERE extract_valid_year(disaster_date) IS NOT NULL
    GROUP BY year
    ORDER BY year;
    """
    return execute_query(query)


def get_disasters_number():
    query = """
    SELECT
    COUNT(*) AS total_incidents
    FROM public.imported_documents,
    unnest(xpath('/airplane_disasters/category/country/disaster', xml)) AS disasters;
    """

    return execute_query(query)


def get_disaster_count_by_aircraft_type():
    query = """
    SELECT
        aircraft_type_text,
        COUNT(*) AS disaster_count
    FROM (
        SELECT xpath('./aircraft_type/@text', x)::TEXT AS aircraft_type_text
        FROM (
            SELECT unnest(xpath('//disaster', xml)) AS x
            FROM imported_documents
        ) AS disasters
    ) AS aircraft_types
    GROUP BY aircraft_type_text
    ORDER BY disaster_count DESC;
    """

    return execute_query(query)