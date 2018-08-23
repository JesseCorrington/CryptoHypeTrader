from webapp.server import dev_server
from sys import argv

config = "dev"
if len(argv) >= 2:
    config = argv[1]

dev_server.run(config)
