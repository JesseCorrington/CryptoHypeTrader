# README #

This README would normally document whatever steps are necessary to get your application up and running.

### Developer Setup ###


## Dependencies
* Install [Python](https://www.python.org/downloads/) 3.6 or newer
* [mongoDB](https://www.mongodb.com/download-center?jmp=nav#community)

## configuration
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

## Local Database setup


# How to run ingestion

```
cd <repo>
./scripts/rundb.sh
python_ 
```

# Monitoring ingestion tasks
localhost:5000/admin.txt


### Data sources
reddit.com (API)
redditmetrics.com (web scraping)
coinmarketcap.com (API and web scraping)

# Future data sources
Twitter (API)
bitcointalk
4chan/biz