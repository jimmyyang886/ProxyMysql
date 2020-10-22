#!/bin/bash
(crontab -l ; echo "*/6 * * * * /home/spark/PycharmProjects/Proxy2mySQL/proxy_get.sh >/dev/null 2>&1") | crontab - 

