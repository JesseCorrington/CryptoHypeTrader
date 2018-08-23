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
* Install [NodeJS](https://nodejs.org/en/download/)
* Clone this repo and install Python requirements
```bash
git clone git@bitbucket.org:jcorrington/cryptohypetrader.git
cd CryptoHypeTrader
./scripts/install_requirements.sh

```


### API keys
You'll need to create several API keys before you can get ingestion running.

#### Reddit API
Go to https://www.reddit.com/prefs/apps and select "create another app..." to create the keys. 

#### Twitter API
Go to https://apps.twitter.com/, apply for a developer account, and create a new app.

#### StockTwits API
Go to https://api.stocktwits.com/developers/apps and register a new application.

### Configuration
Create a file <repo>/ingestion/config.py with the following info:

```python
dev = True

icon_dir = "icons"

reddit = {
    "client_id": "reddit-id",
    "client_secret": "reddit-secret",
    "user_agent": "python-praw"
}

twitter = {
    "api_key": "twitter-key",
    "api_secret": "twitter-secret",
    "access_token": "twitter-token",
    "access_token_secret": "twitter-token-secret"
}

stocktwits = {
    "token": "stocktwits-token"
}

database = {
    "host": "localhost",
    "port": 27017,
    "name": "hype-db"
}
```


## Usage

### Running Ingestion

start the local mongo db,  run `./scripts/rundb.sh`

`python3 main.py -t <task-name>`

Tasks
```
coin_list - Update the list of cryptocurrencies with metadata and icons
historical - Import historical data (price, volume, subreddit subscriber counts)
current - Import current data (price, volume, subreddit subscriber count, subreddit subscribers active, recent reddit comments
twitter - Import recent twitter comments with sentiment analysis
analysis - Create summaries for each coin showing how price, volume, and social stats have grown over time
cc_stats - Import the current stats for each coin from cryptocompare
db_stats - Save current database size statistics for tracking growth and projecting storage needs
stocktwits - Import the current comments with sentiment from StockTwits
```

The progress of ingestion tasks can be monitored through a web UI, see the web client docs below for details.

### Running the web client
Running the web client requires running a local mongodb instance, an API server, and launching the Vue app in development mode.

#### API Server setup
Create the configuration file `<repo>/webapp/server/config.py` with the following info:

```
prod = {
    "database": {
        "host": "production-host",
        "port": production-port,
        "name": "hype-db",
    }
}

dev = {
    "database": {
            "host": "localhost",
            "port": 27017,
            "name": "hype-db",
        }
}
```

#### Run the API server
Run the server `python3 <repo>/web_server.py <dev | prod>`

#### Launch the client web app (Vue app)
in a separate terminal window
`cd <repo>/webapp/client`
`npm install`
`npm start`
http://localhost:8080 in a browser

### Monitor ingestion tasks
* run `python ./webapp/server/dev_server`
* Point your browser to [localhost:5000/admin.txt](http://localhost:5000/admin.html)


### Unit Testing
run `<repo>/scripts/run_tests.sh` to run all of the unit tests


### Server Setup
TODO

### Deployment
TODO



### Data sources
* [Reddit](https://www.reddit.com/dev/api/)
* [Twitter](https://developer.twitter.com/en/docs.html)
* [StockTwits](https://api.stocktwits.com/developers/docs)
* [Redditmetrics](https://www.redditmetrics.com) (web scraping)
* [Coinmarketcap](https://www.coinmarketcap.com) (API and web scraping)

### Potential future data sources
* [bitcointalk.org](https://www.bitcointalk.org)
* [4chan/biz](https://www.4chan.org/biz)


## References
* [pytrader](https://github.com/owocki/pytrader)
* [Algorithmic Trading of Cryptocurrency Based on Twitter Sentiment Analysis](http://cs229.stanford.edu/proj2015/029_report.pdf) 
* [Sentiment Analysis of Twitter Data for Predicting Stock Market Movements](https://arxiv.org/pdf/1610.09225.pdf)
* [Twitter mood predicts the stock market](https://arxiv.org/pdf/1010.3003.pdf)
* [Automated Bitcoin Trading via Machine Learning Algorithms](http://ai2-s2-pdfs.s3.amazonaws.com/e065/3631b4a476abf5276a264f6bbff40b132061.pdf)
* [Bayesian regression and Bitcoin](https://arxiv.org/pdf/1410.1231v1.pdf)
