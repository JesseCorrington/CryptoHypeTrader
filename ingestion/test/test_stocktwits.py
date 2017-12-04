from unittest import TestCase
from ingestion.datasources import stocktwits as st
from ingestion import tasks
from ingestion import manager as mgr

import pandas as pd
import numpy as np


# Initialize coinlist object and grab a sweet list of coins
# coinlist = st.CoinList()
# stocktwits_coins = coinlist.ScrapeCoins()
# stocktwits_coins = coinlist.find_ids()
# coins = st.get_coins()
# coins.symbol[:5]
# for coin in coins.symbol:
#     print(coin+'.X')



# Grab most recent posts for a coin
# ticker = st.Ticker()
# posts = ticker.parse()

# Test out the entire process
mgr.run_tasks(tasks.ImportStockTwits('stocktwits'))
