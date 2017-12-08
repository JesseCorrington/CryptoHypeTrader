from ingestion import datasource as ds
from ingestion import database as db

coins = db.get_coins()
for coin in coins:
    print(coin['symbol'])
