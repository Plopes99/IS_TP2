import asyncio
import time
import uuid
import psycopg2

import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from utils.to_xml_converter import CSVtoXMLConverter

def get_csv_files_in_input_folder():
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(CSV_INPUT_PATH) for f in filenames if
            os.path.splitext(f)[1] == '.csv']

def generate_unique_file_name(directory):
    return f"{directory}/{str(uuid.uuid4())}.xml"
async def get_database_connection():
    try:
        connection = psycopg2.connect(
            user="is",
            password="is",
            host="db-xml",
            port="5432",
            database="is"
        )
        return connection
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        return None

def convert_csv_to_xml(in_path, out_path):
    converter = CSVtoXMLConverter(in_path)
    file = open(out_path, "w")
    file.write(converter.to_xml_str())

class CSVHandler(FileSystemEventHandler):
    def __init__(self, input_path, output_path):
        self._output_path = output_path
        self._input_path = input_path

        # generate file creation events for existing files
        for file in [os.path.join(dp, f) for dp, dn, filenames in os.walk(input_path) for f in filenames]:
            event = FileCreatedEvent(os.path.join(CSV_INPUT_PATH, file))
            event.event_type = "created"
            self.dispatch(event)

    async def convert_csv(self, csv_path):
        # here we avoid converting the same file again
        # !TODO: check converted files in the database
        if csv_path in await self.get_converted_files():
            return

        print(f"new file to convert: '{csv_path}'")

        # we generate a unique file name for the XML file
        xml_path = generate_unique_file_name(self._output_path)

        convert_csv_to_xml(csv_path, xml_path)
        print(f"new xml file generated: '{xml_path}'")

        connection = await get_database_connection()
        if connection is not None:
            try:
                with connection, connection.cursor() as cursor:

                    with open(xml_path, 'r') as xml_file:
                        xml_content = xml_file.read()

                    cursor.execute('INSERT INTO imported_documents (file_name, xml) VALUES (%s, %s)', (xml_path, xml_content))
                    connection.commit()
                    print(f"XML document stored in the imported_documents table")

                    cursor.execute('INSERT INTO converted_documents (src, file_size, dst) VALUES (%s, %s, %s)', (csv_path, os.path.getsize(csv_path),xml_path))
                    connection.commit()
                    print(f"Details from the XML were stored in the converted_documents table")



            except psycopg2.IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    print("XML document already inserted in converted_documents table")
                else:
                    raise

            except Exception as e:

                print(f"Other error: {e}")

            finally:
                connection.close()

    async def get_converted_files(self):
        # !TODO: you should retrieve from the database the files that were already converted before
        connection = await get_database_connection()
        if connection is not None:
            try:
                cursor = connection.cursor()

            # Fetch the file names from the converted_documents table
                cursor.execute('SELECT dst FROM converted_documents')
                converted_files = [record[0] for record in cursor.fetchall()]
                print(converted_files[0])
                return converted_files

            except Exception as e:
                print(f"Error fetching converted files: {e}")
                return []


            finally:
                if connection is not None:
                    connection.close()


    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            asyncio.run(self.convert_csv(event.src_path))


if __name__ == "__main__":

    CSV_INPUT_PATH = "/csv"
    XML_OUTPUT_PATH = "/xml"

    # create the file observer
    observer = Observer()
    observer.schedule(
        CSVHandler(CSV_INPUT_PATH, XML_OUTPUT_PATH),
        path=CSV_INPUT_PATH,
        recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

