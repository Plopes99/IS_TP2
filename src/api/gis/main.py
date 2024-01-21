import sys

import psycopg2
from flask import Flask, request, jsonify

PORT = int(sys.argv[1]) if len(sys.argv) >= 2 else 9000

app = Flask(__name__)
app.config["DEBUG"] = True


def db_connection():
    return psycopg2.connect(
        host='db-rel', database='is', user='is', password='is'
    )


def update_data(query, params=None, fetch_all=False):
    try:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            if fetch_all:
                return cur.fetchall()
            else:
                return cur.fetchone()

    except Exception as err:
        print(f"Erro ao executar a consulta: {err}")
        return None


@app.route('/api/entity/<uuid:idEntity>', methods=['PATCH'])
def update_entity(idEntity):
    try:
        with db_connection() as conn:

            patch_data = request.json

        update_query = """ INSERT INTO disaster (id, date, geom, aircraft_type, operator, fatalities, country_id, updated_on)
                           VALUES ( %s, %s, %s, %s, %s, %s, %s, now())
                           ON CONFLICT (id) DO UPDATE
                           SET
                              date = EXCLUDED.date,
                              geom = EXCLUDED.geom,
                              aircraft_type = EXCLUDED.aircraft_type,
                              operator = EXCLUDED.operator,
                              fatalities = EXCLUDED.fatalities,
                              country_id = EXCLUDED.country_id,
                              updated_on = NOW()
                           RETURNING *; """

        updated_entity = update_data(
            update_query,
            (
                idEntity,
                patch_data.get('date'),
                patch_data.get('geom'),
                patch_data.get('aircraft_type'),
                patch_data.get('operator'),
                patch_data.get('fatalities'),
                patch_data.get('country_id')
            ),
            fetch_all=False
        )

        if not updated_entity:
            return jsonify({'error': 'failed update'})

        conn.commit()

        return jsonify(updated_entity)

    except Exception as err:
        return jsonify({'error': str(err)})


@app.route('/api/title', methods=['GET'])
def get_title():
    try:
        netLng = request.args.get('netLng')
        netLat = request.args.get('netLat')
        swLng = request.args.get('swLng')
        swLat = request.args.get('swLat')

        envelope = f"ST_MakeEnvelope({netLng}, {netLat}, {swLng}, {swLat}, 4326)"  # Assuming 4326 is the SRID for WGS 84

        # Connecting to the database
        conn = psycopg2.connect(host='db-rel', database='is', user='is', password='is')
        cur = conn.cursor()

        envelop_query = f"""
        SELECT jsonb_build_object(
            'type', 'Feature',
            'id', id,
            'geometry', ST_AsGeoJSON(geom)::jsonb,
            'properties', to_jsonb(t.*) - 'id' - 'geom'
        ) AS json
        FROM disasters t
        WHERE t.geom && {envelope}
        """

        cur.execute(envelop_query)
        rows = cur.fetchall()

        # Format the result into JSON
        data = [{'json': row[0]} for row in rows]
        return jsonify(data)

    except psycopg2.Error as err:
        print(f"Psycopg2 Database Error: {err}")
        return jsonify({'error': str(err)})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)
