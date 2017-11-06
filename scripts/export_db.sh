#!/usr/bin/env bash
mongoexport --host localhost --db hype-db --collection coins --type=csv  --out coins.csv --fields symbol,name,subreddit
mongoexport --host localhost --db hype-db --collection prices --type=csv  --out prices.csv --fields date,symbol,open,close,high,low,volume,marketCap
mongoexport --host localhost --db hype-db --collection social_stats --type=csv  --out social_stats.csv --fields date,symbol,reddit_subscribers