#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import boto3
from botocore.exceptions import ClientError
from dateutil import parser
import csv
import pymysql
from time import sleep
import datetime
import warnings
import time,datetime

def get_credential_report(iam_client):
    resp1 = iam_client.generate_credential_report()
    if resp1['State'] == 'COMPLETE' :
        try: 
            response = iam_client.get_credential_report()
            credential_report_csv = response['Content']
            # print(credential_report_csv)
            reader = csv.DictReader(credential_report_csv.splitlines())
            # print(reader.fieldnames)
            credential_report = []
            for row in reader:
                credential_report.append(row)
            return(credential_report)
        except ClientError as e:
            print("Unknown error getting Report: " + e.message)
    else:
        sleep(2)
        return get_credential_report(iam_client)

def get_password_age(credential_report,user):
    for row in credential_report:

        if row['user'] == user:
            if row['password_enabled'] == 'true':
                password_last_changed = parser.parse(row['password_last_changed']).strftime("%Y-%m-%d %H:%M:%S")
                password_last_day = time.mktime(datetime.datetime.strptime(password_last_changed, "%Y-%m-%d %H:%M:%S").timetuple())
                current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())                       
                current_day = time.mktime(datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S").timetuple())

                active_days = (current_day - password_last_day)/60/60/24
                password_age = int(active_days)
            else:
                password_age = -1
    return password_age

#def get_last_activity(credential_report,user):

#    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())                       
#    current_day = time.mktime(datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S").timetuple())

#    for row in credential_report:

#        if row['user'] == user:
#            if row['password_enabled'] == 'true' and row['password_last_used'] != 'no_information':
#                password_last_changed = parser.parse(row['password_last_used']).strftime("%Y-%m-%d %H:%M:%S")
#                password_last_day = time.mktime(datetime.datetime.strptime(password_last_changed, "%Y-%m-%d %H:%M:%S").timetuple())

#                active_days = (current_day - password_last_day)/60/60/24
#                last_activity = str(int(active_days))
#            elif row['password_enabled'] == 'true' and row['password_last_used'] == 'no_information':
#                last_activity = 'None'
#            elif row['password_enabled'] == 'false' and row['access_key_1_active'] == 'true' and row['access_key_2_active'] == 'true':
#                last_activity_lst = []
#                last_activity_1_time = parser.parse(row['access_key_1_last_used_date']).strftime("%Y-%m-%d %H:%M:%S")
#                last_activity_1_date = time.mktime(datetime.datetime.strptime(last_activity_1_time, "%Y-%m-%d %H:%M:%S").timetuple()) 
#                active_days_1 = (current_day - last_activity_1_date)/60/60/24
#                last_activity_lst.append(active_days_1)
#                last_activity_2_time = parser.parse(row['access_key_1_last_used_date']).strftime("%Y-%m-%d %H:%M:%S")
#                last_activity_2_date = time.mktime(datetime.datetime.strptime(last_activity_2_time, "%Y-%m-%d %H:%M:%S").timetuple()) 
#                active_days_2 = (current_day - last_activity_2_date)/60/60/24
#                last_activity_lst.append(active_days_2)
#                last_activity = str(min(last_activity_lst))

#            elif row['password_enabled'] == 'false' and row['access_key_1_active'] == 'true' and row['access_key_2_active'] == 'false':
#                last_activity_time = parser.parse(row['access_key_1_last_used_date']).strftime("%Y-%m-%d %H:%M:%S")
#                last_activity_date = time.mktime(datetime.datetime.strptime(last_activity_time, "%Y-%m-%d %H:%M:%S").timetuple()) 
#                active_days = (current_day - last_activity_date)/60/60/24    
#                last_activity = str(int(active_days))
#            else:
#                last_activity = 'None'

#    return last_activity

    

def export_iam_users_2_Mysql(aws_tag, dbhost, dbport, dbuser, dbpasswd, dbname):

    conn = pymysql.connect(host=dbhost, port=int(dbport), user=dbuser, passwd=dbpasswd, db=dbname, charset='utf8mb4')

    session1 = boto3.session.Session(profile_name=aws_tag, region_name='us-east-1')
    client1 = session1.client('iam')
    response1 = client1.list_users()
    #print response1
    credential_report = get_credential_report(client1)

    #create a table in mysql
    try:
        cursor = conn.cursor()
        # with conn.cursor() as cursor:

        table_name = aws_tag + '_iam_users'
        CheckTable = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (Name varchar(50), \
                                                                    Groupname varchar(256), \
                                                                    Access_key_age int(5), \
                                                                    Password_age int(100), \
                                                                    Last_activity int(5), \
                                                                    mfa varchar(100), \
                                                                    MysqlRecordTime datetime) CHARSET=utf8 COLLATE=utf8_general_ci;"
        ClearTable = "TRUNCATE TABLE `" + table_name + "`;"

        print("Checking and Clearing table: " + table_name)
        cursor.execute(CheckTable)
        cursor.execute(ClearTable)

        current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())                       
        current_day = time.mktime(datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S").timetuple())

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")



            for user in response1['Users']:

                try:


                    activity_date_list = []

                    #get access_key_age, refer to https://stackoverflow.com/questions/45156934/getting-access-key-age-aws-boto3
                    if client1.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']:      #一个人可能有多个access_key
                        all_the_age = []
                        for key in client1.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']:
                            access_key_create_date = key['CreateDate']
                            access_key_date = access_key_create_date.strftime("%Y-%m-%d %H:%M:%S")
                            access_key_day = time.mktime(datetime.datetime.strptime(access_key_date, "%Y-%m-%d %H:%M:%S").timetuple())

                            active_days = (current_day - access_key_day)/60/60/24
                            access_key_age = int(active_days)
                            all_the_age.append(access_key_age)

                            if client1.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])['AccessKeyLastUsed'].has_key('LastUsedDate'):
                                last_activity_key = client1.get_access_key_last_used(AccessKeyId=key['AccessKeyId'])['AccessKeyLastUsed']['LastUsedDate']
                                last_activity_key_date = last_activity_key.strftime("%Y-%m-%d %H:%M:%S")
                                last_activity_key_day = time.mktime(datetime.datetime.strptime(last_activity_key_date, "%Y-%m-%d %H:%M:%S").timetuple())

                                active_days_key = (current_day - last_activity_key_day)/60/60/24
                                #print(user['UserName'] + ' access key: ' + key['AccessKeyId'] + " last used: " + str(int(active_days_key)))
                                activity_date_list.append(int(active_days_key))
                        access_key_age = max(all_the_age)
                    else:
                        access_key_age = -1

                    #注意:client1.list_users()返回的CreateDate并不是access_key的更新时间,使用client1.list_access_keys(UserName='xuedong.li')返回的才是正确的值
                    #if user.has_key('CreateDate'):
                    #    access_key_date = user['CreateDate'].strftime("%Y-%m-%d %H:%M:%S")
                    #    access_key_day = time.mktime(datetime.datetime.strptime(access_key_date, "%Y-%m-%d %H:%M:%S").timetuple())
 
                    #    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())                       
                    #    current_day = time.mktime(datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S").timetuple())

                    #    active_days = (current_day - access_key_day)/60/60/24
                    #    access_key_age = str(int(active_days))
                    #else:
                    #    access_key_age = 'None'

                    password_age = get_password_age(credential_report,user['UserName'])

                    

                    #如果有密码,获得最后一次使用密码(距今)的日期
                    if user.has_key('PasswordLastUsed'):
                        password_date = user['PasswordLastUsed'].strftime("%Y-%m-%d %H:%M:%S")
                        password_day = time.mktime(datetime.datetime.strptime(password_date, "%Y-%m-%d %H:%M:%S").timetuple())

                        active_days = (current_day - password_day)/60/60/24
                        #print(user['UserName'] + ' password last used: ' + str(int(active_days)))
                        activity_date_list.append(int(active_days))

                    #get groups from username
                    if client1.list_groups_for_user(UserName=user['UserName'])['Groups']:
                        group_list = []
                        for group in client1.list_groups_for_user(UserName=user['UserName'])['Groups']:
                            group_list.append(group['GroupName'])
                        groups = ','.join(group_list)
                        #print groups
                    else:
                        groups = 'None'

                    #last_activity = get_last_activity(credential_report,user['UserName'])
                    #print(user['UserName'] + '-----' + str(activity_list))

                    if activity_date_list:
                        last_activity = min(activity_date_list)
                    else:
                        last_activity = -1

                    #get MFA device
                    if client1.list_mfa_devices(UserName=user['UserName'])['MFADevices'] and client1.list_mfa_devices(UserName=user['UserName'])['MFADevices'][0]['SerialNumber'].startswith('arn:aws:iam'):
                        mfa = 'Virtual'
                    elif client1.list_mfa_devices(UserName=user['UserName'])['MFADevices']:
                        mfa = 'Hardware'
                    else:
                        mfa = 'Not_enabled'
                    
                    #
                    # 
                    # print(user['UserName'] + '-----' + access_key_age + '-----' + password_age + '-----' + last_activity + '-----' + groups + '------' + mfa)

                    InsertData = "INSERT INTO `" + table_name + "` (Name, Groupname, Access_key_age, Password_age, Last_activity, mfa, MysqlRecordTime) VALUES (%s, %s, %s, %s, %s, %s, %s);"
                    cursor.execute(InsertData,[user['UserName'], groups, access_key_age, password_age, last_activity, mfa, datetime.datetime.now(), ])

                except Exception as error:
                    print error
                    exit(1)
                conn.commit()
    finally:
        conn.close()
