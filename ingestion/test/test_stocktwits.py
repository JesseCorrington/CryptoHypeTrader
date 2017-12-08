from unittest import TestCase
from ingestion.datasources import stocktwits as st
from ingestion import tasks
from ingestion import manager as mgr

import pandas as pd
import numpy as np


# Initialize coinlist object and grab a list of coins
coinlist = st.CoinList()
stocktwits_coins = coinlist.get()
stocktwits_coins


# Grab most recent posts for a coin
# recentPosts = st.recentPosts()


# Test out the entire process
# mgr.run_tasks(tasks.ImportStockTwits('stocktwits'))
