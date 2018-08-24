#!/usr/bin/env bash
cd webapp/client
npm run build
scp -r ./dist/static root@206.189.218.109:/var/www/html
scp -r ./dist/index.html root@206.189.218.109:/var/www/html/index.html