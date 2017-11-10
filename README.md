# Crypto Hype Trader

Crypto Hype Trader is a project that aims to use social network data to
predict future cryptocurrency price movements. The cryptocurrency markets are extremely volatile,
and many coins have low enough volume that prices can swing wildly based on hype, news, or rumours.
The goal is to collect social network statistics from a variety of sources (ie: reddit, twitter, bitcointak, 4chan/biz)
daily and store it in a database. This data can then be used in the development of algorithmic trading strategies
by either using traditional technical analysis and trading signals or machine learning techniques. Once trading strategies are developed
they can be backtested to check for profitability.
 


## Developer Setup


### Dependencies
* Install [Python](https://www.python.org/downloads/) 3.6 or newer
* Install [mongoDB community edition](https://www.mongodb.com/download-center?jmp=nav#community)

* Clone this repo and install Python requirements
```bash
git clone git@bitbucket.org:jcorrington/cryptohypetrader.git
cd CryptoHypeTrader
./scripts/install_requirements.sh

```

### Configuration
If you don't already have a reddit api key, you'll need to go to https://www.reddit.com/prefs/apps
and select "create another app..." to create the keys. Then create a file <repo>/ingestion/config.py with the following info:

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
* Point your browser to [localhost:5000/admin.txt](http://localhost:5000/admin.html)


### Data sources
* [reddit API](https://www.reddit.com/dev/api/)
* [redditmetrics](https://www.redditmetrics.com) (web scraping)
* [coinmarketcap](https://www.coinmarketcap.com) (API and web scraping)

#### Future data sources
* [twitter](https://www.twitter.com)
* [bitcointalk.org](https://www.bitcointalk.org)
* [4chan/biz](https://www.4chan.org/biz)


## References
* [pytrader](https://github.com/owocki/pytrader)
* [Algorithmic Trading of Cryptocurrency Based on Twitter Sentiment Analysis](http://cs229.stanford.edu/proj2015/029_report.pdf) 
* [Sentiment Analysis of Twitter Data for Predicting Stock Market Movements](https://arxiv.org/pdf/1610.09225.pdf)
* [Twitter mood predicts the stock market](https://arxiv.org/pdf/1010.3003.pdf)
* [Automated Bitcoin Trading via Machine Learning Algorithms](http://ai2-s2-pdfs.s3.amazonaws.com/e065/3631b4a476abf5276a264f6bbff40b132061.pdf)
* [Bayesian regression and Bitcoin](https://arxiv.org/pdf/1410.1231v1.pdf)