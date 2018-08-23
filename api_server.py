from webapp.server import main
from sys import argv

config = "dev"
if len(argv) >= 2:
    config = argv[1]

main.run(config)
