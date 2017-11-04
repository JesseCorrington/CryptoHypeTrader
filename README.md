# Crypto Hype Trader

Crypto Hype Trader is a project that aims to use social network data to
predict future cryptocurrency price movements. The cryptocurrency markets are extremely volatile,
and many coins have low enough volume that prices can swing wildly based on hype, news, or rumours.
The goal is to collect social network statistics from a variety of sources, (ie: reddit, twitter, bitcointak, 4chan/biz)
daily and store it in a database. This data can then be used in the development of algorithmic trading strategies
by either using traditional technical analysis and trading signals or machine learning techniques. Once trading strategies are developed
they can be backtested to check for profitability.
 


## Developer Setup


### Dependencies
* Install [Python](https://www.python.org/downloads/) 3.6 or newer
* Install [mongoDB community edition](https://www.mongodb.com/download-center?jmp=nav#community)

* Clone repo and install Python requirements
```bash
git clone git@bitbucket.org:jcorrington/cryptohypetrader.git
cd CryptoHypeTrader
./scripts/install_requirements.sh

```

### configuration
Create a file <repo>/ingestion/config.py with the following info

```python
reddit = {
    "client_id": "your_id",
    "client_secret": "your_secret",
    "user_agent": "python-praw"
}

database = {
    "host": "localhost",
    "port": 27017,
    "name": "hype-db"
}
```


## Usage
### Startup the local database
run `./scripts/rundb.sh`


### Run data ingestion
run `python ./ingestion/tasks.py`

### Monitor ingestion tasks
* run `python ./webapp/server/dev_server`
* Point your browser to [localhost:5000/admin.txt](localhost:5000/admin.txt)


### Data sources
* [reddit API](https://www.reddit.com/dev/api/)
* [redditmetrics](redditmetrics.com) (web scraping)
* [coinmarketcap](coinmarketcap.com) (API and web scraping)

#### Future data sources
* [twitter](twitter.com)
* [bitcointalk.org](bitcointalk.org)
* [4chan/biz](4chan.org/biz)


## References
[Algorithmic Trading of Cryptocurrency Based on Twitter Sentiment Analysis](http://cs229.stanford.edu/proj2015/029_report.pdf) 
