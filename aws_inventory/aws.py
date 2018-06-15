#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import os
import argparse
import ConfigParser
from init_env import Prepare_ENV
from export_ec2 import GetInstanceName,GetInstance,ExportInstance2Mysql
from export_route53 import ExportZone2Mysql
from export_s3 import ExportS3_2_Mysql
from export_elasticbeanstalk import Export_Elastic_Beanstalk_2_Mysql
from export_iam import export_iam_users_2_Mysql
from export_domain import export_domain_2_Mysql

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export AWS instance to a MYSQL.')
    parser.add_argument("-c","--config",default='config.ini',action="store",dest='config_file',
                        help='define a configure file. DEFAULT=config.ini')
    args = parser.parse_args()
    print("Reading From: " + args.config_file)

    if not args.config_file or not os.path.exists(args.config_file):
        parser.error('Configuration file DO NOT EXISTS.')

    Config = ConfigParser.ConfigParser()
    Config.read(args.config_file)

    aws_tag = Config.get("aws","aws_tag")
    aws_region = Config.get("aws","region")
    aws_access_key_id = Config.get("aws","aws_access_key_id")
    aws_secret_access_key = Config.get("aws","aws_secret_access_key")
    mysql_server = Config.get("mysql","server")
    mysql_port = Config.get("mysql","port")
    mysql_user = Config.get("mysql","user")
    mysql_passwd = Config.get("mysql","passwd")
    mysql_db = Config.get("mysql","db")

    Prepare_ENV(args.config_file, aws_tag, aws_region, aws_access_key_id, aws_secret_access_key)

    InstanceList = GetInstance(aws_tag)
    print("Got " + str(len(InstanceList)) + " Instances from [" + aws_tag + "] which defined in ~/.aws/credentials." )
    print("Export Instances to Mysql...")
    ExportInstance2Mysql(aws_tag, mysql_server, mysql_port, mysql_user, mysql_passwd, mysql_db, InstanceList)
    print("Done.")

    print("Export HostedZones and RecordSets to Mysql...")
    ExportZone2Mysql(aws_tag, mysql_server, mysql_port, mysql_user, mysql_passwd, mysql_db)
    print("Done.")

    ExportS3_2_Mysql(aws_tag, mysql_server, mysql_port, mysql_user, mysql_passwd, mysql_db)
    Export_Elastic_Beanstalk_2_Mysql(aws_tag, mysql_server, mysql_port, mysql_user, mysql_passwd, mysql_db)

    print("Export IAM to Mysql...")
    export_iam_users_2_Mysql(aws_tag, mysql_server, mysql_port, mysql_user, mysql_passwd, mysql_db)
    print("Done.")

    print("Export Domain information")
    domain_list = ['grindr.com', 'grindr.io', 'grindrguy.net', 'grindrguy.com', 'grindrstore.com', 'intomore.com', 'grindr.pe', 'grindr.com.br', 'grindr.com.ve','grindr.pt', 'xtraapp.com']
    export_domain_2_Mysql(domain_list, mysql_server, mysql_port, mysql_user, mysql_passwd, mysql_db)
    print("Done.")
