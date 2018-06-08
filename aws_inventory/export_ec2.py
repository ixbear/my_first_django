#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import boto3
import pymysql
import datetime
import warnings

def GetInstanceName(list):
    instanceName = 'None'
    for tag in list:
        if tag['Key'] == 'Name':
            instanceName = tag['Value']
    #print("InstanceName is " + instanceName )
    return instanceName

def GetInstance(aws_tag):

    InstanceList = []
    session1 = boto3.session.Session(profile_name=aws_tag, region_name='us-east-1')
    client1 = session1.client('ec2')
    response1 = client1.describe_instances()

    for reservation in response1["Reservations"]:
        for i in reservation['Instances']:

            # print i.keys()

            # 请注意,如果对应的key不存在(例如KeyName,PublicIpAddress等),则会报错
            if not i.has_key('KeyName'):
                i['KeyName'] = "None"
            if not i.has_key('PublicIpAddress'):
                i['PublicIpAddress'] = "None"
            if not i.has_key('VpcId'):
                i['VpcId'] = "None"
            if not i.has_key('PrivateIpAddress'):
                i['PrivateIpAddress'] = "None"

            #get instance name
            if not i.has_key('Tags'):
                print(i['InstanceId'] + " do not have a Tags.")
                instanceName = "None"
            else:
                instanceName = GetInstanceName(i['Tags'])

            if not i.has_key('SubnetId'):
                i['SubnetId'] = "None"

            SecurityGroup = []     # 安全组可能有多个
            VolumeDict = {}         #磁盘可能有多个, 使用 { /dev/sda1:vol-xxxx, /dev/sda2:vol-xxxx } 的方式来展示

            for eachGroup in i['SecurityGroups']:
                SecurityGroup.append(eachGroup['GroupName'])
            for eachBlock in i['BlockDeviceMappings']:
                VolumeDict[eachBlock['DeviceName']] = eachBlock['Ebs']['VolumeId']   #add a /dev/sda1:vol-xxxxxx的记录到VolumeDict

            #print i['InstanceId'], i['Hypervisor'], i['KeyName'], i['VpcId'], i['PrivateIpAddress'], i['PublicIpAddress'], SecurityGroup

            aInstance = [
                    instanceName,
                    i['InstanceId'],
                    i['InstanceType'],
                    i['Hypervisor'],
                    i['VirtualizationType'],
                    i['State']['Name'],
                    i['KeyName'],
                    i['VpcId'],
		            i['SubnetId'],
                    i['PrivateIpAddress'],
                    i['PublicIpAddress'],
                    i['LaunchTime'],
                    i['ImageId'],
                    VolumeDict,
                    SecurityGroup
            ]
            InstanceList.append(aInstance)
    return InstanceList

def ExportInstance2Mysql(aws_tag, dbhost, dbport, dbuser, dbpasswd, dbname, InstanceList):
    conn = pymysql.connect(host=dbhost, port=int(dbport), user=dbuser, passwd=dbpasswd, db=dbname, charset='utf8mb4')
    table_name = aws_tag + '_ec2_Instances'
    try:
        cursor = conn.cursor()
        #with conn.cursor() as cursor:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")

            CheckTable = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (InstanceName varchar(50), \
                                                                        InstanceId VARCHAR(30) NOT NULL, \
                                                                        InstanceType varchar(20), \
                                                                        Hypervisor varchar(20), \
                                                                        VirtualizationType varchar(20), \
                                                                        Status varchar(15), \
                                                                        KeyName varchar(30), \
                                                                        VpcId varchar(20), \
                                                                        SubnetId varchar(50), \
                                                                        PrivateIpAddress varchar(18), \
                                                                        PublicIpAddress varchar(18), \
                                                                        LaunchTime datetime, \
                                                                        ImageId varchar(100), \
                                                                        VolumeDict varchar(256), \
                                                                        SecurityGroup varchar(256), \
                                                                        MysqlRecordTime datetime) CHARSET=utf8 COLLATE=utf8_general_ci;"
            ClearTable = "TRUNCATE TABLE `" + table_name + "`"
            InsertData = "INSERT INTO `" + table_name + "` (InstanceName, InstanceId, InstanceType, Hypervisor, VirtualizationType, Status, KeyName, VpcId, SubnetId, PrivateIpAddress, PublicIpAddress, LaunchTime, ImageId, VolumeDict, SecurityGroup, MysqlRecordTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

            print("Checking and Clearing table: " + table_name)
            cursor.execute(CheckTable)
            cursor.execute(ClearTable)

            for eachInstance in InstanceList:
                #print type(eachInstance[0]),type(eachInstance[1]),type(eachInstance[2]),type(eachInstance[3]),type(eachInstance[4]),type(eachInstance[5]),type(eachInstance[6]),type(eachInstance[7]),type(eachInstance[8]),type(eachInstance[9]),type(eachInstance[10]),type(eachInstance[11])
                #print eachInstance[13], type(eachInstance[13])
                cursor.execute(InsertData,[
                                            eachInstance[0],
                                            eachInstance[1],
                                            eachInstance[2],
                                            eachInstance[3],
                                            eachInstance[4],
                                            eachInstance[5],
                                            eachInstance[6],
                                            eachInstance[7],
                                            eachInstance[8],
                                            eachInstance[9],
                                            eachInstance[10],
                                            eachInstance[11],
                                            eachInstance[12],
                                            str(eachInstance[13]),
                                            str(eachInstance[14]),
                                            datetime.datetime.now(),

                ])
            conn.commit()
    finally:
        conn.close()