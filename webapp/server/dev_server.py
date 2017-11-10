import flask
import os
import json
from bson import ObjectId
from datetime import datetime

# TODO: prob want to move database out of ingestion module, maybe
from ingestion import database as db

# This is just a basic dev server for easy internal testing
# Basic REST API access is provided to the database with Eve,
# and static files are hosted out of the client directory

cwd = os.path.dirname(os.path.realpath(__file__))
public_dir = cwd + "/../client"

domain = {
    'coins': {},
    'prices': {},
    'ingestion_tasks': {},
    'social_stats': {},
}

settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'hype-db',
    'DOMAIN': domain,
    'ALLOW_UNKNOWN': True,
    'URL_PREFIX': "api",
    'PAGINATION': False
}

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.timestamp() * 1000

        return json.JSONEncoder.default(self, o)





app = flask.Flask(__name__)

@app.route('/<path:path>')
def static_proxy(path):
    return flask.send_from_directory(public_dir, path)


def to_bool(s):
    return s.lower() == "true"


@app.route('/api/ingestion_tasks')
def get_tasks():
    running = flask.request.args.get("running")
    query = {}
    if running:
        query["running"] = to_bool(running)

    items = db.MONGO_DB.ingestion_tasks.find(query)
    l = list(items)

    return JSONEncoder().encode(l)

app.run()
