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
