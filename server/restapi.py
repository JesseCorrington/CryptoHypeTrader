from eve import Eve
from flask import send_from_directory

import os
cwd = os.path.dirname(os.path.realpath(__file__))

domain = {
    'prices': {},
    'social_stats': {}
}

settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'hype-db',
    'DOMAIN': domain,
    'ALLOW_UNKNOWN': True,
    'URL_PREFIX': "api"
}

public_dir = cwd + "../client"

public_dir = "/Users/jesse/dev/CryptoHypeTrader/client"

print("public dir is: ", public_dir)

app = Eve(__name__, settings=settings, static_url_path=public_dir)

@app.route('/')
def index():
    print("* serving static file")
    return send_from_directory(public_dir, 'test.html')

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return send_from_directory(public_dir, path)

app.run()

