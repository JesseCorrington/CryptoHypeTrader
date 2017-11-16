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
    mgr.run_tasks(tasks.ImportCoinList())


def import_historic_data():
    mgr.run_tasks(tasks.historical_data_tasks())


def import_current_data():
    mgr.run_tasks(tasks.current_data_tasks())


def main():
    from sys import argv
    opts = getopts(argv)

    if "-t" in opts:
        task_name = opts["-t"]
    else:
        print("Error: must specificy -mode")
        return

    task_map = {
        "coin_list": import_coin_list,
        "historic": import_historic_data,
        "current": import_current_data
    }

    if task_name not in task_map:
        print("Error: task {} should be one of {}".format(task_name, list(task_map.keys())))
        return

    task_map[task_name]()


if __name__ == "__main__":
    main()
