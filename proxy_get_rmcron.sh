#!/bin/bash
#crontab -l > mycron
#echo "*/6 * * * * /home/spark/PycharmProjects/Proxy2mySQL/proxy_get.sh >/dev/null 2>&1" >>mycron
crontab -l | grep -v '/home/spark/PycharmProjects/Proxy2mySQL/proxy_get.sh'  | crontab -
