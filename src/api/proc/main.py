import sys

import psycopg2
import xmlrpc.client
from flask import Flask

PORT = int(sys.argv[1]) if len(sys.argv) >= 2 else 9000

app = Flask(__name__)
app.config["DEBUG"] = True

server = xmlrpc.client.ServerProxy("http://rpc-server:9000")


@app.route('/api/disaster_by_year', methods=['GET'])
def get_disaster_by_year():
    data = server.xml_data_manipulation.get_disaster_by_year()
    return data, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)