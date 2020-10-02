# ProxyMysql
proxy availability test by Multiprocessing and MySQL.  

# crontab  
*/6 * * * * cd /home/spark/PycharmProjects/Proxy2mySQL && ./proxy_get.sh >/dev/null 2>&1

# build Docker image

docker build -t jimmyyang886/proxy_cycling .

#connect to host mysql server

docker run --rm --network="host" jimmyyang886/proxy_cycling



