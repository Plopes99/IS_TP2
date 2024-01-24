import base64
import signal
import sys
import os

print(sys.path)

from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer

from functions.csv_to_xml_converter import CSVtoXMLConverter
from functions.validator import validator
from functions.import_documents import import_documents
from functions.save_xml_file import save_xml_file
from functions.clear_database import clear_database
from functions.xml_data_manipulation import (get_disaster_by_year,
                                             get_disasters_number,
                                             get_disaster_count_by_aircraft_type,)



b = os.path.abspath("C:/Users/35191/IPVC/3ano/IS/PycharmProjects/IS_TP1/src/rpc-server/functions/")
sys.path.append(b)
print(sys.path)

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


with SimpleXMLRPCServer(('rpc-server', 9000), requestHandler=RequestHandler, allow_none=True) as server:
    server.register_introspection_functions()


    def signal_handler():
        print("received signal")
        server.server_close()

        print("exiting, gracefully")
        sys.exit(0)

    def get_converter():
        return CSVtoXMLConverter("../data/aviation_accidents.csv")

    def to_xml_str():
        return get_converter().to_xml_str()

    def get_xml_data():
        return get_converter().to_xml_str()

    def validate_xml(xml_path):
        xsd_path = "xml_schema.xsd"
        result = validator(xml_path, xsd_path)
        print("Validação concluída.")
        return result


    # signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # register both functions
    server.register_function(get_converter, 'get_converter')
    server.register_function(to_xml_str, 'to_xml_str')
    server.register_function(get_xml_data, 'get_xml_data')
    server.register_function(validate_xml, 'validate_xml')
    server.register_function(import_documents)
    server.register_function(get_disaster_by_year)
    server.register_function(get_disaster_count_by_aircraft_type)
    server.register_function(get_disasters_number)
    server.register_function(save_xml_file)
    server.register_function(clear_database)

    # start the server
    print("Starting the RPC Server...")
    server.serve_forever()