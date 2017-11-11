from ingestion import tasks

def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


def main():
    from sys import argv
    opts = getopts(argv)
    if "-m" in opts:
        run_mode = opts["-m"]
    else:
        print("Error: must specificy -mode")
        return

    if run_mode == "historic":
        tasks.import_historic_data()
    elif run_mode == "current":
        tasks.import_current_data()
    else:
        print("Error: invalid run mode", run_mode)


if __name__ == "__main__":
    main()