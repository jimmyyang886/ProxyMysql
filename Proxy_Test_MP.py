from multiprocessing import Process, Pool, freeze_support
import os, time
import requests
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
from bs4 import BeautifulSoup


import requests
from requests.exceptions import ProxyError, ConnectTimeout, SSLError, ReadTimeout
from datetime import datetime

engine = create_engine("mysql+pymysql://teb101Club:teb101Club@localhost/twstock??charset=utf8mb4", max_overflow=5)

def ip_port_crawler():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    resp = requests.get('https://free-proxy-list.net', headers=headers, timeout=(5, 1))
    soup = BeautifulSoup(resp.text, 'lxml')
    trs = soup.find('table').select('tr')

    ip_port_list = set()

    for i in range(1, len(trs) - 1):
        tds = trs[i].find_all('td')
        if tds[6].text == 'yes':
            ip_port = tds[0].text + ':' + tds[1].text
            # ping test
            response = os.system("ping -c 1 " + ip_port)
            # print(ip_port, response)
            if response == 1:
                ip_port_list.add(ip_port)
    return ip_port_list


# ip_port_list=ip_port_crawler()
# iplist=ip_port_crawler()
# df.tail()

def check_existence():
    query = "SELECT * FROM FreeProxy;"
    exist = list(engine.execute(query))
    ip_port_list = set()
    for _exist in exist:
        ip, port, active = _exist[0], _exist[1], _exist[2]
        response = os.system("ping -c 1 " + ip + ':' + str(port))
        ip_port_list.add(ip + ':' + str(port))
        # print(ip_port, response)
        if response == 1:
            # print(ip, port, active)
            if active == "no":
                query = "update FreeProxy SET active='yes'" + "WHERE ip='" + ip + "' and port=" + str(port) + ';'
                print("update active state from no to yes:", query)
                engine.execute(query)
        else:
            query = "update FreeProxy SET active='no'" + "WHERE ip='" + ip + "' and port=" + str(port) + ';'
            print("update active state from yes to no", query)
            engine.execute(query)
    return ip_port_list


def Webtest(inputs):
    #engine = create_engine("mysql+pymysql://teb101Club:teb101Club@120.97.27.92/twstock??charset=utf8mb4", max_overflow=5)
    uname, url, proxies = inputs[0],  inputs[1], inputs[2]
    #print(proxies.get('http').split(':'))
    ip = proxies.get('http').split(':')[0]
    port = proxies.get('http').split(':')[1]

    #print(ip, port)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    try:
        r = requests.get(url=url, headers=headers, proxies=proxies, verify=False, timeout=5)
        # print (_iport, r.status_code)
        if r.status_code == 200:
            # print("connection ok")
            query = "update FreeProxy SET {} ='yes' WHERE ip='{}' and port={};" \
                .format(uname, ip, port)
            # print(query)
            print("update {}:{} state to yes".format(ip, port))
            engine.execute(query)
        else:
            query = "update FreeProxy SET active= 'no', {} ='no' WHERE ip='{}' and port={};" \
                .format(uname, ip, port)
            print("update {}:{} state to no".format(ip, port))
            engine.execute(query)

    except ProxyError:
        # print ("ProxyError:", _iport)
        query = "update FreeProxy SET active='no', {} ='ProxyError' WHERE ip='{}' and port={};" \
            .format(uname, ip, _port)
        print("update {} state to ProxyError".format(ip, port))
        engine.execute(query)
        # print(e)

    except SSLError:
        # print ("ProxyError:", _iport)
        query = "update FreeProxy SET {}='no', {} ='SSLError' WHERE ip='{}' and port={};" \
            .format(active, uname, ip, port)
        print("update {} state to SSLError".format(ip, port))
        engine.execute(query)

    except ConnectTimeout:
        query = "update FreeProxy SET active='no', {} ='ConnectTimeout' WHERE ip='{}' and port={};" \
            .format(uname, ip, port)
        print("update {} state to ConnectTimeout".format(ip, port))
        engine.execute(query)

    except ReadTimeout:
        query = "update FreeProxy SET active='no', {} ='ReadTimeout' WHERE ip='{}' and port={};" \
            .format(uname, ip, port)
        print("update {} state to ReadTimeout".format(ip, port))
        engine.execute(query)

    except Exception as e:
        query = "update FreeProxy SET active='no', {} ='UFO' WHERE ip='{}' and port={};" \
            .format(uname, ip, port)
        print("update {} state to ReadTimeout".format(ip, port))
        engine.execute(query)


def proxy_arg(uname, url):
    query = "SELECT ip, port FROM FreeProxy WHERE active = 'yes';"
    proxy_list=[]

    # print(list(engine.execute(query)))
    for _iport in list(engine.execute(query)):
        http = _iport[0] + ':' + str(_iport[1])
        https = _iport[0] + ':' + str(_iport[1])

        proxies = {
            'http': http,
            'https': https,
        }
        proxy_list.append([uname, url, proxies])

    return proxy_list



if __name__ == '__main__':


    exist = check_existence()
    new = ip_port_crawler()


    for _diff in new.difference(exist):

        query = "Insert INTO  FreeProxy (ip, port, DF, active) VALUES ('{}',{},'{}','yes');" \
            .format(_diff.split(':')[0], _diff.split(':')[1], datetime.now().isoformat())
        #print(query)
        print("Insert New Proxy:",_diff.split(':')[0], _diff.split(':')[1] )
        engine.execute(query)

    #freeze_support()

    pool = Pool(2)
    uname = 'ChinaTime'
    url = "http://www.chinatimes.com/?chdtv"

    inputs=proxy_arg(uname, url)

      # 運行多處理程序

    pool_outputs = pool.map(Webtest, inputs)