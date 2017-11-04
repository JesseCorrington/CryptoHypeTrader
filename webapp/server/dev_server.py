from eve import Eve
import flask
import os

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

app = Eve(__name__, settings=settings)

@app.route('/<path:path>')
def static_proxy(path):
    return flask.send_from_directory(public_dir, path)


app.run()
