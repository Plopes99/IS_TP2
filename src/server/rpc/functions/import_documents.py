import psycopg2
import xml.etree.ElementTree as ET
from datetime import datetime


def import_documents(file_name, xml_file):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(user="is",
                                      password="is",
                                      host="is-db",
                                      port="5432",
                                      database="is")

        cursor = connection.cursor()

        with open(xml_file, encoding='utf-8') as file:
            data = file.read()

        # INSERIR O FICHEIRO XML
        cursor.execute("INSERT INTO imported_documents(file_name, xml) VALUES(%s,%s)", (file_name, data))

        tree = ET.parse(xml_file)
        root = tree.getroot()
        for category_elem in root.findall('.//category'):
            category_name = category_elem.attrib.get('name', '')
            accidents_types = category_elem.attrib.get('accident_type', '')
            damage_types = category_elem.attrib.get('damage_type', '')

            # airplane_disasters
            cursor.execute(
                "INSERT INTO airplane_disasters (category_name, accidents_types, damage_types) VALUES (%s, %s, %s) RETURNING id",
                (category_name, accidents_types, damage_types)
            )
            category_id = cursor.fetchone()[0]

            for country_elem in category_elem.findall('.//country'):
                country_name = country_elem.attrib.get('name', '')

                # COUNTRIES
                cursor.execute(
                    "INSERT INTO countries (country_name, category_id) VALUES (%s, %s) RETURNING id",
                    (country_name, category_id)
                )
                country_id = cursor.fetchone()[0]

                for disaster_elem in country_elem.findall('.//disaster'):
                    date_elem = disaster_elem.find('date')
                    aircraft_type_elem = disaster_elem.find('aircraft_type')
                    operator_elem = disaster_elem.find('operator')
                    fatalities_elem = disaster_elem.find('fatalities')

                    # Verifica se os elementos estão presentes antes de acessar seus atributos
                    date_text = date_elem.attrib.get('text', '') if date_elem is not None else ''
                    aircraft_type_text = aircraft_type_elem.attrib.get('text',
                                                                       '') if aircraft_type_elem is not None else ''
                    operator_text = operator_elem.attrib.get('text', '') if operator_elem is not None else ''
                    fatalities_text = fatalities_elem.attrib.get('text', '') if fatalities_elem is not None else ''

                    # Converte a data para o formato adequado
                    try:
                        date = datetime.strptime(date_text, "%d-%b-%Y").date() if date_text else None
                    except ValueError:
                        date = None

                    fatalities = int(fatalities_text) if fatalities_text and fatalities_text.isdigit() else None

                    # DISASTERS
                    cursor.execute(
                        "INSERT INTO disasters (date, aircraft_type, operator, fatalities, country_id) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (date, aircraft_type_text, operator_text, fatalities, country_id)
                    )

        connection.commit()

    except (Exception, psycopg2.Error) as error:
        error_message = f"Failed to fetch data: {error}"
        if hasattr(error, 'pgcode') and hasattr(error, 'pgerror'):
            error_message += f" (PGCode: {error.pgcode}, PGError: {error.pgerror})"

        return error_message

    finally:
        if connection:
            cursor.close()
            connection.close()
