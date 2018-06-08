#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import boto3
import pymysql
import datetime
import warnings

def ExportZone2Mysql(aws_tag, dbhost, dbport, dbuser, dbpasswd, dbname):

    conn = pymysql.connect(host=dbhost, port=int(dbport), user=dbuser, passwd=dbpasswd, db=dbname, charset='utf8mb4')

    session1 = boto3.session.Session(profile_name=aws_tag, region_name='us-east-1')
    client1 = session1.client('route53')
    response1 = client1.list_hosted_zones()

    #print response1

    #create a table in mysql, table name format: Zone_mydomain.com
    try:
        cursor = conn.cursor()
        # with conn.cursor() as cursor:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")

            for eachZone in response1['HostedZones']:

                # print eachZone['Name'], eachZone['Id']     #得到主域名及其ZoneId
                # table_name = aws_tag + "_Zone_" + eachZone['Name'].replace('-','_').replace('.','_')  #表名不允许有-和., 所以用_替换
                table_name = aws_tag + "_Zone_[" + eachZone['Name'] + "]_Id_[" + eachZone['Id'].replace('/hostedzone/','') + "]"
                CheckTable = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (Name varchar(50), Type VARCHAR(30), Value varchar(256), TTL varchar(10), MysqlRecordTime datetime) CHARSET=utf8 COLLATE=utf8_general_ci;"
                ClearTable = "TRUNCATE TABLE `" + table_name + "`;"

                print("Checking and Clearing table: " + table_name)
                cursor.execute(CheckTable)
                cursor.execute(ClearTable)

                #response2 = client1.list_resource_record_sets(HostedZoneId=eachZone['Id'])
                #直接调用client1.list_resource_record_sets方法会导致只返回100条记录,详见https://stackoverflow.com/questions/41716586/aws-route-53-listing-cname-records-using-boto3
                paginator = client1.get_paginator('list_resource_record_sets')
                try:
                    source_zone_records = paginator.paginate(HostedZoneId=eachZone['Id'])
                    for record_set in source_zone_records:
                        for record in record_set['ResourceRecordSets']:
                            if not record.has_key('TTL'):
                                record['TTL'] = 'None'
                            if record.has_key('AliasTarget'):
                                Value = record['AliasTarget']['DNSName']
                            elif record.has_key('ResourceRecords'):
                                Value = ','.join(v['Value'] for v in record['ResourceRecords'])
                            else:
                                Value = 'Null'

                            # print record['Name'],record['Type'], Value, record['TTL']   #打印出每个二级子域名的解析信息

                            InsertData = "INSERT INTO `" + table_name + "` (Name, Type, Value, TTL, MysqlRecordTime) VALUES (%s, %s, %s, %s, %s);"
                            cursor.execute(InsertData,[record['Name'], record['Type'], Value, record['TTL'], datetime.datetime.now(), ])

                except Exception as error:
                    print ('An error occured getting source zone records: ' + str(error))
                    exit(1)

                #for i in response2['ResourceRecordSets']:
                #    #ValueList = []
                #    if not i.has_key('TTL'):
                #        i['TTL'] = 'None'
                #    if i.has_key('AliasTarget'):
                #        ValueList = i['AliasTarget']['DNSName']
                #    elif i.has_key('ResourceRecords'):
                #        ValueList = ','.join(v['Value'] for v in i['ResourceRecords'])
                #    else:
                #        ValueList = 'Null'

                    #print i['Name'],i['Type'], ValueList, i['TTL']   #打印出每个二级子域名的解析信息

                #    InsertData = "INSERT INTO `" + table_name + "` (Name, Type, Value, TTL, MysqlRecordTime) VALUES (%s, %s, %s, %s, %s);"
                #    cursor.execute(InsertData, [i['Name'], i['Type'], ValueList, i['TTL'], datetime.datetime.now(),])
                conn.commit()
    finally:
        conn.close()