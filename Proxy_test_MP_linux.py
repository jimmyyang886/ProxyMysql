from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ProxyError, ConnectTimeout, SSLError, ReadTimeout
from datetime import datetime
import time
import os
#import sqlalchemy
import pymysql
from multiprocessing import Pool

engine = create_engine("mysql+pymysql://teb101Club:teb101Club@localhost/twstock??charset=utf8mb4", max_overflow=5)

def ip_port_crawler():
    url='https://free-proxy-list.net'
    print('crawl new free list from', url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    resp = requests.get(url=url, headers=headers, timeout=(5, 2))
    soup = BeautifulSoup(resp.text, 'lxml')
    trs = soup.find('table').select('tr')

    ip_port_set = set()

    for i in range(1, len(trs) - 1):
        tds = trs[i].find_all('td')
        if tds[6].text == 'yes':
            ip_port = tds[0].text + ':' + tds[1].text
            # ping test
            #response = os.system("ping -c 1 " + ip_port)
            #response = os.system("nc -vz " +ds[0].text + ' '+ds[0].text)
            #print(ip_port, response)
            #if response == 0:
            ip_port_set.add(ip_port)
    return ip_port_set


# ip_port_list=ip_port_crawler()
# iplist=ip_port_crawler()
# df.tail()

def check_existence():
    query = "SELECT ip, port,active FROM freeproxy;"
    exist = list(engine.execute(query))
    ip_port_set = set()
    for _exist in exist:
        ip, port, active = _exist[0], _exist[1], _exist[2]
        #response = os.system("ping -c 1 " + ip + ':' + str(port))
        #response = os.system("nc -vz " + ip + ' ' + str(port)) #for linux : response =0 if success
        ip_port_set.add(ip + ':' + str(port))
        #print(ip, port, response)
        #if response == 0:
            #print(ip, port, active)
        #     if active == "no":
        #         query = "update freeproxy SET active='yes'" + "WHERE ip='" + ip + "' and port=" + str(port) + ';'
        #         print("update active state from no to yes:", query)
        #         engine.execute(query)
        # else:
        #     query = "update freeproxy SET active='no'" + "WHERE ip='" + ip + "' and port=" + str(port) + ';'
        #     print("update active state from yes to no", query)
        #     engine.execute(query)
    return ip_port_set


def Webtest(inputs):
    #engine = create_engine("mysql+pymysql://teb101Club:teb101Club@localhost/twstock??charset=utf8mb4", max_overflow=5)
    uname, url, proxies = inputs[0],  inputs[1], inputs[2]
    #print(proxies)
    ip = proxies.get('http').replace('http://','').split(':')[0]
    port = proxies.get('http').replace('http://','').split(':')[1]
    #print(uname, ip, port)
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    #headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv: 79.0) Gecko/20100101 Firefox/79.0'}
    #print('proxy_test:', proxies)
    try:
        r = requests.get(url=url, headers=headers, proxies=proxies, verify=False, timeout=(5, 2))

        if r.status_code == 200:
            # print("connection ok")
            query = "update freeproxy SET active='yes', {} ='yes' WHERE ip='{}' and port={};" \
                .format(uname, ip, port)
            # print(query)
            print("update {}:{} state to yes".format(ip, port))
            engine.execute(query)
        else:
            query = "update freeproxy SET active= 'no', {} ='no' WHERE ip='{}' and port={};" \
               .format(uname, ip, port)
            print("update {}:{} state to no".format(ip, port))
            engine.execute(query)

    except ProxyError:
        pass
        #print ("ProxyError:", iport)
        query = "update freeproxy SET active='no', {} ='ProxyError' WHERE ip='{}' and port={};" \
           .format(uname, ip, port)
        print("update {}:{} state to ProxyError".format(ip, port))
        engine.execute(query)

    except SSLError:
        # print ("ProxyError:", iport)
        query = "update freeproxy SET 'active'='no', {} ='SSLError' WHERE ip='{}' and port={};" \
            .format(uname, ip, port)
        print("update {}:{} state to SSLError".format(ip, port))
        engine.execute(query)

    except ConnectTimeout:
        query = "update freeproxy SET active='no', {} ='ConnectTimeout' WHERE ip='{}' and port={};" \
            .format(uname, ip, port)
        print("update {}:{} state to ConnectTimeout".format(ip, port))
        engine.execute(query)

    except ReadTimeout:
        query = "update freeproxy SET active='no', {} ='ReadTimeout' WHERE ip='{}' and port={};" \
            .format(uname, ip, port)
        print("update {}:{} state to ReadTimeout".format(ip, port))
        engine.execute(query)

    except Exception as e:
        query = "update freeproxy SET active='no', {} ='UFO' WHERE ip='{}' and port={};" \
            .format(uname, ip, port)
        print("update {}:{} state to UFO".format(ip, port))
        engine.execute(query)


def proxy_arg(uname, url):
    #query = "SELECT ip, port FROM freeproxy WHERE active = 'yes';"
    query = "SELECT ip, port FROM freeproxy;"
    proxy_list=[]
    # print(list(engine.execute(query)))
    for _iport in list(engine.execute(query)):
        http = 'http://'+_iport[0] +':' + str(_iport[1])
        https ='https://'+_iport[0] +':' + str(_iport[1])

        proxies = {
            'http': http,
            'https': https,
        }
        proxy_list.append([uname, url, proxies])
    return proxy_list

if __name__ == '__main__':

    #query = "SELECT ip, port,active FROM freeproxy;"
    #exist = list(engine.execute(query))

    # 運行多處理程序
    #print('check existence', exist)
    #pool = Pool(4)
    #pool_outputs = pool.map(check_existence, exist)

    exist = check_existence()
    new = ip_port_crawler()

    print('update new proxy......')
    for _diff in new.difference(exist):
        query = "Insert INTO freeproxy (ip, port, DF, active) VALUES ('{}',{},'{}','yes');" \
            .format(_diff.split(':')[0], _diff.split(':')[1], datetime.now().isoformat())
        #print(query)
        print("Insert New Proxy:",_diff.split(':')[0], _diff.split(':')[1] )
        engine.execute(query)

    print('update state of proxy.....')

    uname = 'ChinaTime'
    url = "http://www.chinatimes.com/?chdtv"
    inputs = proxy_arg(uname, url)
    #print(inputs)
    #
    #運行多處理程序
    pool = Pool(8)
    pl= pool.map(Webtest, inputs)
    # pool.close()
    # pool.join()
    # print(pl)
