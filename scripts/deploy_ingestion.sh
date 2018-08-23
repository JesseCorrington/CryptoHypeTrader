#!/usr/bin/env bash
scp -r ./common root@138.68.231.32:~/cryptohypetrader
scp -r ./ingestion root@138.68.231.32:~/cryptohypetrader
scp ./main.py root@138.68.231.32:~/cryptohypetrader/main.py
