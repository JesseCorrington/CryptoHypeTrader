from unittest import TestCase
from ingestion.datasources import stocktwits as st
from ingestion import tasks
from ingestion import manager as mgr
from ingestion import database as db
from ingestion.tasks import ImportCoinList

import pandas as pd
import numpy as np


# Initialize coinlist object and grab a list of coins
# coinlist = st.CoinList()
# stocktwits_coins = coinlist.get()
# # stocktwits_coins
# coinlist.failed_matches.iloc[1, 2]
# stocktwits_coins

# coins = coinlist.stocktwits_coin_meta


# Grab most recent posts for a coin
# recentPosts = st.recentPosts()


# Test out the entire process
mgr.run_tasks(tasks.ImportStockTwits('stocktwits'))
