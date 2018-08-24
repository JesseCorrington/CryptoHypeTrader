#!/usr/bin/env bash
scp -r ./common root@206.189.218.109:~/cryptohypetrader
scp ./webapp/server/main.py root@206.189.218.109:~/cryptohypetrader/webapp/server/main.py
scp ./api_server.py root@206.189.218.109:~/cryptohypetrader/api_server.py