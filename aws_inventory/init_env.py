#!/usr/bin/python
# -*- coding:UTF-8 -*-
__author__ = "https://zhukun.net"

import os
import ConfigParser

def Prepare_ENV(config_file, aws_tag, region, aws_access_key_id, aws_secret_access_key):

    print("sync info to ~/.aws/credentials from " + config_file)
    home_dir=os.path.expanduser('~')
    config1 = ConfigParser.ConfigParser()
    config1.read(home_dir + "/.aws/credentials")
    if aws_tag not in config1.sections():
        config1.add_section(aws_tag)
        config1.set(aws_tag, 'aws_access_key_id', aws_access_key_id)
        config1.set(aws_tag, 'aws_secret_access_key', aws_secret_access_key)
        with open(home_dir + '/.aws/credentials', 'wb') as configfile:
            config1.write(configfile)
    else:
        config1.set(aws_tag, 'aws_access_key_id', aws_access_key_id)
        config1.set(aws_tag, 'aws_secret_access_key', aws_secret_access_key)
        with open(home_dir + '/.aws/credentials', 'wb') as configfile:
            config1.write(configfile)