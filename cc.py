from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from novaclient.client import Client
from datetime import datetime, timedelta
import pymysql
import traceback
import requests
import json
import yaml
import os


USERNAME = ""
PASSWORD = ""
DOMAIN = ""
PROJECT_ID = ""
AUTH_URL = ""
DATABASE = "/etc/openstack/MySQL.db"
OPENRC = "/etc/openstack/openrc"

with open(OPENRC) as f:
    openrc = yaml.safe_load(f)
    for k, v in openrc.items():
        exec(f"{k}='{v}'")

def __get_token():
    data = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "name": USERNAME,
                        "domain": {
                            "name": DOMAIN
                        },
                        "password": PASSWORD
                    }
                }
            }
        }
    }
    url = AUTH_URL+"/auth/tokens"
    token = requests.post(url,json=data).headers["x-subject-token"]
    return token

def main():
    ip_name_list = []
    auth = v3.Token(auth_url=AUTH_URL,
                    token=__get_token())

    sess = session.Session(auth=auth,
                           verify=False)
    nova = Client(2, session=sess)
    for server in nova.servers.list():
        server_name = server.name
        for _, vl in  nova.servers.ips(server).items():
            for v in vl:
                server_ip = v['addr']
                ip_name_list.append([server_ip, server_name])
    for server_ip ,server_name in ip_name_list:
        print(f"{server_ip}\t{server_name}")
    # try to load data into database if db info configured.
    if os.path.exists(DATABASE):
        try:
            with open(DATABASE) as f:
                db = yaml.safe_load(f)
            table = db.pop("table")
            with pymysql.connect(**db) as cursor:
                cursor.execute(f"TRUNCATE {table}")
                cursor.executemany(f"INSERT INTO {table} (ip_addr, hostname) VALUES (%s, %s)", ip_name_list)
        except Exception:
            pass

if __name__ == '__main__':
    main()
