# Crypto Hype Trader

Crypto Hype Trader is a project that aims to use social network data to
predict future cryptocurrency price movements. The cryptocurrency markets are extremely volatile,
and many coins have low enough volume that prices can swing wildly based on hype, news, or rumours.
The goal is to collect social network statistics from a variety of sources (ie: reddit, twitter, bitcointak, 4chan/biz)
daily and store it in a database. This data can then be used in the development of algorithmic trading strategies
by either using traditional technical analysis and trading signals or machine learning techniques. Once trading strategies are developed
they can be backtested to check for profitability.

Visit http://cryptohypetrader.com for the latest production deployment


## Developer Setup

### Dependencies
* Install [Python](https://www.python.org/downloads/) 3.6 or newer
* Install [mongoDB community edition](https://www.mongodb.com/download-center?jmp=nav#community)
* Install [NodeJS](https://nodejs.org/en/download/)
* Clone this repo and install Python requirements
```bash
git clone git@github.com:JesseCorrington/CryptoHypeTrader.git
cd CryptoHypeTrader
./scripts/install_requirements.sh

```


### API keys
You'll need to create several API keys before you can get ingestion running.

##### Reddit API
Go to https://www.reddit.com/prefs/apps and select "create another app..." to create the keys. 

##### Twitter API
Go to https://apps.twitter.com/, apply for a developer account, and create a new app.

##### StockTwits API
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

First start the local mongo db with `./scripts/rundb.sh`

Then run an ingestion task by doing `python3 main.py -t <task-name>`

##### Tasks
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

The progress of ingestion tasks can be monitored through the web client on the admin page, see the web client docs below for details.

### Running the web client
Running the web client requires running a local mongodb instance, an API server, and launching the Vue app in development mode.

##### API Server setup
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

##### Run the API server
run `python3 <repo>/api_server.py dev`

##### Launch the client web app (Vue app)
In a separate terminal window do:

`cd <repo>/webapp/client`

`npm install`

`npm start`

Open http://localhost:8080 in a browser


### Unit Testing
run `<repo>/scripts/run_tests.sh` to run all of the unit tests


### Server Setup
The production deployment is hosted on Digital Ocean using two droplets.

The backend droplet (db.crypohypetrader.com) hosts mongodb and runs ingestion tasks. Cron is used for the scheduling of ingestion tasks to run on regular time intervals, see `<repo>/server_setup/cront.txt` for the schedule. Deployment is done by running `./scripts/deploy_ingestion`. The cron setup must be manually copied over if it changes.

The second droplet (cryptohypetrader.com) is the front end server and hosts a web api server and an nginx front end web server. nginx is the entry point for all HTTP requests, and serves static content for HTML, JS, and CSS, and proxies `/api` requests on to the api server. Caching is enabled in nginx to reduce the number of calls that get through to the api server and subsequently have to call out to the database server. From the client side the application is read only on the database, and data isn't chaning very fast, so this can allow a high level of scaling. The api server is a python flask app run with Gunicorn and uses `num_cores + 1` for the number of processes. Deployment is done by running `./scripts/deploy_api_server` and `./scripts/deploy_client`. Deploying the api server requires restarting the gunicorn service.

Further scaling could be accomplished by splitting the back end server into two servers, one for the database, and
another for the ingestion tasks to run. Adding a load balancer and a dynamic number of front end servers would allow horizontal scaling to a very high degree.

![Alt text](/architecture_diagram.png?raw=true "High Level Architecture Diagram")


### Data sources
* [Reddit](https://www.reddit.com/dev/api/)
* [Twitter](https://developer.twitter.com/en/docs.html)
* [StockTwits](https://api.stocktwits.com/developers/docs)
* [Redditmetrics](https://www.redditmetrics.com) (web scraping)
* [Coinmarketcap](https://www.coinmarketcap.com) (API and web scraping)
* [bitcointalk.org](https://www.bitcointalk.org)


## References
* [pytrader](https://github.com/owocki/pytrader)
* [Algorithmic Trading of Cryptocurrency Based on Twitter Sentiment Analysis](http://cs229.stanford.edu/proj2015/029_report.pdf) 
* [Sentiment Analysis of Twitter Data for Predicting Stock Market Movements](https://arxiv.org/pdf/1610.09225.pdf)
* [Twitter mood predicts the stock market](https://arxiv.org/pdf/1010.3003.pdf)
* [Automated Bitcoin Trading via Machine Learning Algorithms](http://ai2-s2-pdfs.s3.amazonaws.com/e065/3631b4a476abf5276a264f6bbff40b132061.pdf)
* [Bayesian regression and Bitcoin](https://arxiv.org/pdf/1410.1231v1.pdf)

## Screenshots

![Alt text](/screenshots/coin_list.png?raw=true "Landing page coin list")
<br><br>
![Alt text](/screenshots/charts1.png?raw=true "Example charts")
<br><br>
![Alt text](/screenshots/charts2.png?raw=true "Example charts")
<br><br>
![Alt text](/screenshots/admin.png?raw=true "Admin page for monitoring ingestion tasks on the server")
