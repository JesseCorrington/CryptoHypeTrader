#!/usr/bin/env bash
cd webapp/client
npm run build
scp -r ./dist/static root@138.68.231.32:/var/www/html
scp -r ./dist/index.html root@138.68.231.32:/var/www/html/index.html