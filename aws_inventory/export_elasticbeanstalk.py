#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import boto3
import pymysql
import datetime
import warnings

def get_instance(env_name,response):
    instance_list = []
    for reservation in response["Reservations"]:
        for i in reservation['Instances']:
            if i.has_key('Tags'):
                for tag in i['Tags']:
                    if tag['Key'] == 'elasticbeanstalk:environment-name' and tag['Value'] == env_name:
                        instance_list.append(i['InstanceId'])
    return instance_list

def Export_Elastic_Beanstalk_2_Mysql(aws_tag, dbhost, dbport, dbuser, dbpasswd, dbname):

    conn = pymysql.connect(host=dbhost, port=int(dbport), user=dbuser, passwd=dbpasswd, db=dbname, charset='utf8mb4')

    session1 = boto3.session.Session(profile_name=aws_tag, region_name='us-east-1')
    client1 = session1.client('elasticbeanstalk')
    response1 = client1.describe_applications()


    client2 = session1.client('ec2')
    response2 = client2.describe_instances()

    #print response1
    table_name = aws_tag + "_Elastic_Beanstalk"
    #print table_name
    app_list = [i['ApplicationName'] for i in response1['Applications']]
    #print app_list

    try:

        cursor = conn.cursor()
        # with conn.cursor() as cursor:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")

            CheckTable = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (Application_Name varchar(50), \
                                                                        Environment_Name VARCHAR(30), \
                                                                        Environment_Id varchar(30), \
                                                                        Environment_CNAME varchar(100), \
                                                                        Environment_Health varchar(30), \
                                                                        Environment_Update_Time datetime, \
                                                                        min_instances varchar(100), \
                                                                        max_instances varchar(100), \
                                                                        remove_instance_when varchar(256), \
                                                                        add_instance_when varchar(256), \
                                                                        instance_type varchar(20), \
                                                                        vpc_id varchar(100), \
                                                                        subnets varchar(256), \
                                                                        image_id varchar(256), \
                                                                        Related_Instances_Count int(2), \
                                                                        Related_Instances varchar(256), \
                                                                        MysqlRecordTime datetime) CHARSET=utf8 COLLATE=utf8_general_ci;"
            ClearTable = "TRUNCATE TABLE `" + table_name + "`;"

            print("Checking and Clearing table: " + table_name)
            cursor.execute(CheckTable)
            cursor.execute(ClearTable)
            for eachApp in app_list:
                env_list = [ e['EnvironmentName'] for e in client1.describe_environments(ApplicationName=eachApp)['Environments']]
                #print env_list

                for eachEnv in env_list:
                    env_detail = client1.describe_environments(ApplicationName=eachApp,EnvironmentNames=[eachEnv,])
                    #print env_detail['Environments'][0]                    
                    env_id = env_detail['Environments'][0]['EnvironmentId']
                    if env_detail['Environments'][0].has_key('CNAME'):
                        env_cname = env_detail['Environments'][0]['CNAME']
                    else:
                        env_cname = ''
                    env_health = env_detail['Environments'][0]['Health']
                    env_update_time = env_detail['Environments'][0]['DateUpdated']
                    related_instances_count = len(get_instance(eachEnv,response2))
                    related_instances = ','.join(get_instance(eachEnv,response2))

                    response3 = client1.describe_configuration_settings(ApplicationName=eachApp,EnvironmentName=eachEnv)['ConfigurationSettings'][0]['OptionSettings']

                    #print response3
                    env_keypair = 'null'
                    env_min_instances = ''
                    env_max_instances = ''
                    env_image_id = 'null'
                    env_instance_type = 'null'
                    env_monitor_interval = 'null'
                    env_lower_threshold = 'null'
                    env_upper_threshold = 'null'
                    env_unit = ''
                    env_statistic = ''
                    env_measure_name = ''
                    env_vpcid = 'null'
                    env_subnets = 'null'
                    for i in response3:
                        if i['OptionName'] == 'EC2KeyName' and i.has_key('Value'):
                            env_keypair = i['Value']
                        if i['OptionName'] == 'MinSize':
                            env_min_instances = i['Value']
                        if i['OptionName'] == 'MaxSize':
                            env_max_instances = i['Value']
                        if i['OptionName'] == 'ImageId':
                            env_image_id = i['Value']
                        if i['OptionName'] == 'InstanceType':
                            env_instance_type = i['Value']
                        if i['OptionName'] == 'MonitoringInterval':
                            env_monitor_interval = i['Value']
                        if i['OptionName'] == 'LowerThreshold':
                            env_lower_threshold = i['Value']
                        if i['OptionName'] == 'UpperThreshold':
                            env_upper_threshold = i['Value']
                        if i['OptionName'] == 'Unit':         #unit means percent
                            env_unit = i['Value']
                        if i['OptionName'] == 'Statistic' and i.has_key('Value'):    #statistic means Average
                            env_statistic = i['Value']
                        if i['OptionName'] == 'MeasureName':  #measure_name means CPUUtilization
                            env_measure_name = i['Value']
                        if i['OptionName'] == 'VPCId' and i.has_key('Value'):
                            env_vpcid = i['Value']
                        if i['OptionName'] == 'Subnets' and i.has_key('Value'):
                            env_subnets = i['Value']


                    #print eachApp, eachEnv, env_id, env_cname, env_health, env_update_time, related_instances_count, related_instances
                    InsertData = "INSERT INTO `" + table_name + "` (Application_Name, \
                                                                Environment_Name, \
                                                                Environment_Id, \
                                                                Environment_CNAME, \
                                                                Environment_Health, \
                                                                Environment_Update_Time, \
                                                                min_instances, \
                                                                max_instances, \
                                                                remove_instance_when, \
                                                                add_instance_when, \
                                                                instance_type, \
                                                                vpc_id, \
                                                                subnets, \
                                                                image_id, \
                                                                Related_Instances_Count, \
                                                                Related_Instances, \
                                                                MysqlRecordTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    cursor.execute(InsertData, [
                                                eachApp,
                                                eachEnv,
                                                env_id,
                                                env_cname,
                                                env_health,
                                                env_update_time,
                                                env_min_instances,
                                                env_max_instances,
                                                env_statistic + ' ' + env_measure_name + ' < ' + env_lower_threshold + ' ' + env_unit,
                                                env_statistic + ' ' + env_measure_name + ' > ' + env_upper_threshold + ' ' + env_unit,
                                                env_instance_type,
                                                env_vpcid,
                                                env_subnets,
                                                env_image_id,
                                                related_instances_count,
                                                related_instances,
                                                datetime.datetime.now(),
                                                ])
            conn.commit()
    finally:
        conn.close()
