from ingestion import manager as mgr
from ingestion import tasks


def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


def import_coin_list():
    mgr.run_tasks([tasks.ImportCoinList(), tasks.DownloadCoinIcons()])


def import_historical_data():
    mgr.run_tasks(tasks.historical_data_tasks())


def import_current_data():
    mgr.run_tasks(tasks.current_data_tasks())


def import_twitter_data():
    mgr.run_tasks(tasks.twitter_tasks())


def analysis_tasks():
    mgr.run_tasks(tasks.analysis_tasks())


def cc_stats_task():
    mgr.run_tasks(tasks.ImportCryptoCompareStats())


def db_stats():
    mgr.run_tasks(tasks.SaveDBStats())


def import_stocktwits():
    mgr.run_tasks(tasks.ImportStockTwits('stocktwits'))


def main():
    """ Run an ingestion task. Must specify -t <task-name>
    -t options
        coin_list - Update the list of cryptocurrencies with metadata and icons
        historical - Import historical data (price, volume, subreddit subscriber counts)
        current - Import current data (price, volume, subreddit subscriber count, subreddit subscribers active, recent reddit comments
        twitter - Import recent twitter comments with sentiment analysis
        analysis - Create summaries for each coin showing how price, volume, and social stats have grown over time
        cc_stats - Import the current stats for each coin from cryptocompare
        db_stats - Save current database size statistics for tracking growth and projecting storage needs
        stocktwits - Import the current comments with sentiment from StockTwits
    """

    from sys import argv
    opts = getopts(argv)

    if "-t" in opts:
        task_name = opts["-t"]
    else:
        print("Error: must specify -t")
        return

    task_map = {
        "coin_list": import_coin_list,
        "historical": import_historical_data,
        "current": import_current_data,
        "twitter": import_twitter_data,
        "analysis": analysis_tasks,
        "cc_stats": cc_stats_task,
        "db_stats": db_stats,
        "stocktwits": import_stocktwits
    }

    if task_name not in task_map:
        print("Error: task {} should be one of {}".format(task_name, list(task_map.keys())))
        return

    tasks.init()

    task_map[task_name]()


if __name__ == "__main__":
    main()
