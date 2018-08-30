from webapp.server.main import app
from sys import argv

# Allow any origin in dev mode
if len(argv) >= 2 and argv[1] == "dev":
    print("Running API Server in dev mode")
    from flask_cors import CORS
    CORS(app)

if __name__ == "__main__":
    app.run()
