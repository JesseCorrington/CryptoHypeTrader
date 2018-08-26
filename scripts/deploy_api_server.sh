#!/usr/bin/env bash
scp -r ./common root@206.189.218.109:~/cryptohypetrader
scp ./webapp/server/main.py root@206.189.218.109:~/cryptohypetrader/webapp/server/main.py
scp ./api_server.py root@206.189.218.109:~/cryptohypetrader/wsgi.py
scp ./server_setup/cryptohypetrader.service root@206.189.218.109:/etc/systemd/system/cryptohypetrader.service
scp ./server_setup/nginx.txt root@206.189.218.109:/etc/nginx/sites-available/cryptohypetrader
