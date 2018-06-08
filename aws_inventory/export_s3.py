#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import boto3
import pymysql
import datetime
import warnings

def ExportS3_2_Mysql(aws_tag, dbhost, dbport, dbuser, dbpasswd, dbname):

    conn = pymysql.connect(host=dbhost, port=int(dbport), user=dbuser, passwd=dbpasswd, db=dbname, charset='utf8mb4')

    session1 = boto3.session.Session(profile_name=aws_tag, region_name='us-east-1')
    client1 = session1.client('s3')
    #client2 = session1.client('lightsail')
    response1 = client1.list_buckets()

    #print response1
    if response1['Owner']['DisplayName'] == aws_tag:
        table_name = response1['Owner']['DisplayName'] + "_S3"
    else:
        print("api returned the DisplayName of S3 is " + response1['Owner']['DisplayName'] + ", not " + aws_tag + " which defined in the configuration file. Will use " + aws_tag + "_S3 as the table name.")
        table_name = aws_tag + "_S3"
    #print table_name

    #create a table in mysql, table name format: Zone_mydomain.com
    try:

        cursor = conn.cursor()
        # with conn.cursor() as cursor:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")

            CheckTable = "CREATE TABLE IF NOT EXISTS `" + table_name + "` (Bucket_Name varchar(100), Bucket_Region VARCHAR(30), Buecket_Region_Name varchar(30), Bucket_Create_Date datetime, Bucket_Website varchar(100), Bucket_Versioning varchar(20), Bucket_MFADelete varchar(20), Buecket_Policy varchar(256), MysqlRecordTime datetime) CHARSET=utf8 COLLATE=utf8_general_ci;"
            ClearTable = "TRUNCATE TABLE `" + table_name + "`;"

            print("Checking and Clearing table: " + table_name)
            cursor.execute(CheckTable)
            cursor.execute(ClearTable)

            for eachBucket in response1['Buckets']:

                bucket_name = eachBucket['Name']
                bucket_create_date = eachBucket['CreationDate']
                bucket_region = client1.get_bucket_location(Bucket=bucket_name)['LocationConstraint']    #get region, such as ap-southeast-1

                #print bucket_region, bool(bucket_region)
                #Note that for buckets created in the US Standard region, us-east-1, the value of LocationConstraint will be null
                if not bucket_region:
                    bucket_region = 'us-east-1'

                #get region_name, such as Virginia, Singapore
                #bucket_region_name = 'Null'
                #region_list = client2.get_regions()
                #for i in region_list['regions']:
                #    if i['name'] == bucket_region:
                #        bucket_region_name = i['displayName']

                #print bucket_name + '....', bucket_region, bucket_region_name
                try:
                    bucket_policy = client1.get_bucket_policy(Bucket=bucket_name)['Policy']
                    #print bucket_policy
                except Exception as error:
                    bucket_policy = "None"
                #print bucket_policy

                try:
                    get_website = client1.get_bucket_website(Bucket=bucket_name)['IndexDocument']
                    # according https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteEndpoints.html
                    # https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_website_region_endpoints
                    if bucket_region in ["us-east-1", "us-west-1", "us-west-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "eu-west-1", "sa-east-1"]:
                        bucket_website = bucket_name + ".s3-website-" + bucket_region + ".amazonaws.com"
                    else:
                        bucket_website = bucket_name + ".s3-website." + bucket_region + ".amazonaws.com"
                except Exception as error:
                    #print error
                    bucket_website = "Disabled"
                #print(bucket_name + "      " + bucket_website)

                #print client1.get_bucket_versioning(Bucket='repo.dsci.grindr.io')
                versioning_dict = client1.get_bucket_versioning(Bucket=bucket_name)
                if versioning_dict.has_key('Status'):
                    bucket_versioning = versioning_dict['Status']
                else:
                    bucket_versioning = 'Disabled'
                if versioning_dict.has_key('MFADelete'):
                    bucket_mfa_delete = versioning_dict['MFADelete']
                else:
                    bucket_mfa_delete = 'Disabled'
                #print bucket_name, bucket_versioning

                InsertData = "INSERT INTO `" + table_name + "` (Bucket_Name, Bucket_Region, Buecket_Region_Name, Bucket_Create_Date, Bucket_Website, Bucket_Versioning, Bucket_MFADelete, Buecket_Policy, MysqlRecordTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(InsertData, [bucket_name, bucket_region, "On_Dev", bucket_create_date, bucket_website,bucket_versioning, bucket_mfa_delete, bucket_policy, datetime.datetime.now(),])
            conn.commit()
    finally:
        conn.close()
