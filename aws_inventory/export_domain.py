#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import ssl, socket
import whois
import pymysql
import datetime
import warnings
import time,datetime

def ssl_expiry_datetime(hostname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    try:
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=hostname,
        )   
        # 3 second timeout because Lambda has runtime limitations
        conn.settimeout(3.0)
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        # parse the string from the certificate into a Python datetime object
        a = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt).strftime('%Y-%m-%d %H:%M:%S')
        return a
    except socket.timeout as error:
        return('time out. may be no ssl.')
    except socket.gaierror as error:
        return('Name or service not known')

def export_domain_2_Mysql(domain_list, dbhost, dbport, dbuser, dbpasswd, dbname):

    conn = pymysql.connect(host=dbhost, port=int(dbport), user=dbuser, passwd=dbpasswd, db=dbname, charset='utf8mb4')
    try:

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
        
            cursor = conn.cursor()
        
            table_name = 'domain_info'
            CheckTable = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (Domain_Name varchar(50), \
                                                                    Domain_Expire_Date varchar(256), \
                                                                    SSL_Expire_Date varchar(128), \
                                                                    Domain_Name_Servers varchar(256), \
                                                                    Domain_Registrar varchar(256), \
                                                                    MysqlRecordTime datetime) CHARSET=utf8 COLLATE=utf8_general_ci;"
            ClearTable = "TRUNCATE TABLE `" + table_name + "`;"

            print("Checking and Clearing table: " + table_name)
            cursor.execute(CheckTable)
            cursor.execute(ClearTable)

            for domain in domain_list:

                domain_expiration_date = 'None'
                domain_registrar = 'None'
                domain_name_servers = 'None'

                try:

                    whois_result = whois.whois(domain)
                    if whois_result.has_key('expiration_date') and isinstance(whois_result.expiration_date, datetime.date):
                        domain_expiration_date = whois_result.expiration_date.strftime('%Y-%m-%d %H:%M:%S')
                    if whois_result.has_key('registrar'):
                        domain_registrar = str(whois_result.registrar)     #if whois_result.registraris null, the default type in not string but NoneType
                    if whois_result.has_key('name_servers') and isinstance(whois_result.name_servers, list):
                        name_servers_list = whois_result.name_servers
                        domain_name_servers = ', '.join(name_servers_list)

                    ssl_expire_date = ssl_expiry_datetime(domain)

                except socket.timeout as error:
                    print(domain + ": " + str(error) + ", continue next domain.")
                except socket.gaierror as error:
                    print(domain + ": " + str(error) + ", continue next domain.")

                #print(domain + '-----' + domain_expiration_date + '-----' + domain_registrar + '-----' + ssl_expire_date + '-----' + domain_name_servers + '------')
                InsertData = "INSERT INTO `" + table_name + "` (Domain_Name, Domain_Expire_Date, SSL_Expire_Date, Domain_Name_Servers, Domain_Registrar, MysqlRecordTime) VALUES (%s, %s, %s, %s, %s, %s);"
                cursor.execute(InsertData,[domain, domain_expiration_date, ssl_expire_date, domain_name_servers, domain_registrar, datetime.datetime.now(), ])

            conn.commit()
    finally:
        conn.close()

