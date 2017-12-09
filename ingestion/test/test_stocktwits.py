from unittest import TestCase
from ingestion.datasources import stocktwits as st
from ingestion import tasks
from ingestion import manager as mgr
from ingestion import config
from common import database as db
from ingestion.tasks import ImportCoinList

import pandas as pd
import numpy as np


# Initialize coinlist object and connect to server
coinlist = st.CoinList()
db.init(config.database)

# Obtain list of coins
coins = coinlist.get()
coins
# Looks at coins that didn't match with symbol_name id
coinlist.initial_failed_matches

# Look at coins that didn't match after entire process
coinlist.final_failed_matches

# Grab most recent posts for a coin
recentPosts = st.recentPosts(coins.symbol[4] + '.X', coins.coin_id[4], coins.name[4]).get()

# Test out the entire process
mgr.run_tasks(tasks.ImportStockTwits('stocktwits'))
