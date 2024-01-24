import sys

import psycopg2
import json
from flask import Flask, request, jsonify
from uuid import UUID

PORT = int(sys.argv[1]) if len(sys.argv) >= 2 else 9000

app = Flask(__name__)
app.config["DEBUG"] = True


def task_update_entity(id, update_data):
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(host='db-rel', database='is', user='is', password='is')
        cur = conn.cursor()

        patch_data = update_data

        update_query = """  INSERT INTO disaster (id, date, geom, aircraft_type, operator, fatalities, country_id, updated_on)
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
                            RETURNING *; 
                        """

        cur.execute(update_query, (
            UUID(id),
            patch_data.get('date'),
            patch_data.get('geom'),
            patch_data.get('aircraft_type'),
            patch_data.get('operator'),
            patch_data.get('fatalities'),
            patch_data.get('country_id')
            )
        )

        updated_entity = cur.fetchone()

        conn.commit()

        return {'message': 'Entidade atualizada com sucesso'}

    except psycopg2.Error as err:
        return {'error': f"Psycopg2 Database Error: {err}"}

    finally:
        if conn:
            conn.close()


@app.route('/api/entity/<uuid:entity_id>', methods=['PATCH'])
def update_entity(entity_id):
    try:
        update_data = request.json

        new_entity = task_update_entity(entity_id, update_data)

        if 'error' in new_entity:
            return jsonify(new_entity), 500
        else:
            return jsonify(new_entity)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/title', methods=['GET'])
def get_title():
    conn = None
    cur = None

    try:
        # retorna os valores do enpoint
        neLng = request.args.get('neLng', type=float)
        neLat = request.args.get('neLat', type=float)
        swLng = request.args.get('swLng', type=float)
        swLat = request.args.get('swLat', type=float)

        conn = psycopg2.connect(host='db-rel', database='is', user='is', password='is')

        cur = conn.cursor()

        envelop_query = f"""
                SELECT jsonb_build_object(
                    'type', 'Feature',
                    'id', id,
                    'geometry', ST_AsGeoJSON(geom)::jsonb,
                    'properties', jsonb_build_object(
                        'date', date,
                        'aircraft_type', aircraft_type,
                        'operator', operator,
                        'fatalities', fatalities,
                        'country_id', country_id)
                ) AS json
                FROM disasters t
                WHERE t.geom && ST_MakeEnvelope({swLng}, {swLat}, {neLng}, {neLat}, 4326)
        """

        cur.execute(envelop_query)
        rows = cur.fetchall()

        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for row in rows:
            feature = {
                "type": "Feature",
                "properties": {
                    "id": row[0],
                    "date": str(row[1]),
                    "aircraft_type": row[3],
                    "operator": row[4],
                    "fatalities": row[5],
                    "country_id": str(row[6]),
                    "imgUrl": "https://cdn-icons-png.flaticon.com/512/1830/1830404.png",
                },
                "geom": json.loads(row[2])
            }
            geojson["features"].append(feature)

        return jsonify(geojson)

    except psycopg2.Error as err:
        print(f"Psycopg2 Database Error: {err}")
        return jsonify({'error': str(err)})

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)
