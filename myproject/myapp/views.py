# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.db import connection
import re

# Create your views here.
#def index(request):
#    context = {
#        'days': [1, 2, 3],
#    }
#    return render(request, 'days.html', context)
def test2(request):

    cursor = connection.cursor()
    context = {}
    domain_key = {}
    for i in connection.introspection.get_table_list(cursor):
        if "_zone_" in i.name.lower() and '_id_' in i.name.lower() and 'production' in i.name.lower():
            zone_id = re.split(r"\[|\]", i.name)[3]
            zone_name = re.split(r"\[|\]", i.name)[1]
            domain_key[zone_id] = zone_name    #注意,可能会有重复的zone_name, 所以zone_name不能作为key

    context['list'] = domain_key

    return render(request, 'days.html', context)

def test_para(request):
    content1 = {}

    content1['absolute_uri'] = request.build_absolute_uri()
    content1['full_path'] = request.get_full_path()

    content1['data_env'] = request.GET.get("env","None")
    content1['data_item'] = request.GET.get("item","None")
    return render(request, 'ec2.html', content1)


def get_production_data(request):
    content1 = {}
    content1['env'] = 'production'
    cursor = connection.cursor()

    domain_dict = {}

    #首先把zone_name和zone_id的表解析一下
    for i in connection.introspection.get_table_list(cursor):
        if "_zone_" in i.name.lower() and '_id_' in i.name.lower() and 'production' in i.name.lower():

            zone_id = re.split(r"\[|\]", i.name)[3].encode('utf8')
            zone_name = re.split(r"\[|\]", i.name)[1].encode('utf8')
            domain_dict[zone_id] = zone_name  # 注意,可能会有重复的zone_name, 所以zone_name不能作为key
    content1['list'] = domain_dict            # 这里domain_dict的格式为{"zone_id1": "zone_name1", "zone_id2": "zone_name2", "zone_id3":"zone_name3"}


    if request.GET.get("item") == "ec2" or not request.GET.get("item"):    #缺省显示EC2的数据

        content1['thead'] = []
        table_name = 'aws.production_ec2_Instances'    #table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))    #.encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)
        return render(request, 'table.html', content1)



    elif request.GET.get("item") == "route53":
        if request.GET.get("id") in content1['list'].keys():
            zone_id = request.GET.get("id")
            zone_name = content1['list'][zone_id]

            table_name = 'aws.production_Zone_['+ zone_name +']_Id_[' + zone_id + ']'
            content1['thead'] = []
            for i in connection.introspection.get_table_description(cursor, table_name):
                content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
            cursor.execute("select * from `" + table_name + "`")
            content1['tbody'] = []
            for each_entry in cursor.fetchall():
                dict = {}
                for each_value in each_entry:
                    dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
                content1['tbody'].append(dict)
            return render(request, 'table.html', content1)
        if not request.GET.get("id"):
            return HttpResponse('404 Error! Usage: ?item=route53&id=[zone_id]')
        else:
            return HttpResponse('404 Error! Not found: ' + request.GET.get("id"))



    elif request.GET.get("item") == "ebs":

        content1['thead'] = []
        table_name = 'aws.production_Elastic_Beanstalk'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "s3":

        content1['thead'] = []
        table_name = 'aws.production_S3'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "iam":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_iam_users'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    else:
        raise Http404()

def get_development_data(request):
    content1 = {}
    content1['env'] = 'development'
    cursor = connection.cursor()

    domain_dict = {}

    #首先把zone_name和zone_id的表解析一下
    for i in connection.introspection.get_table_list(cursor):
        if "_zone_" in i.name.lower() and '_id_' in i.name.lower() and 'development' in i.name.lower():

            zone_id = re.split(r"\[|\]", i.name)[3].encode('utf8')
            zone_name = re.split(r"\[|\]", i.name)[1].encode('utf8')
            domain_dict[zone_id] = zone_name  # 注意,可能会有重复的zone_name, 所以zone_name不能作为key
    content1['list'] = domain_dict            # 这里domain_dict的格式为{"zone_id1": "zone_name1", "zone_id2": "zone_name2", "zone_id3":"zone_name3"}


    if request.GET.get("item") == "ec2" or not request.GET.get("item"):    #缺省显示EC2的数据

        content1['thead'] = []
        table_name = 'aws.development_ec2_Instances'    #table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))    #.encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)
        return render(request, 'table.html', content1)



    elif request.GET.get("item") == "route53":
        if request.GET.get("id") in content1['list'].keys():
            zone_id = request.GET.get("id")
            zone_name = content1['list'][zone_id]

            table_name = 'aws.development_Zone_['+ zone_name +']_Id_[' + zone_id + ']'
            content1['thead'] = []
            for i in connection.introspection.get_table_description(cursor, table_name):
                content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
            cursor.execute("select * from `" + table_name + "`")
            content1['tbody'] = []
            for each_entry in cursor.fetchall():
                dict = {}
                for each_value in each_entry:
                    dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
                content1['tbody'].append(dict)
            return render(request, 'table.html', content1)
        if not request.GET.get("id"):
            return HttpResponse('404 Error! Usage: ?item=route53&id=[zone_id]')
        else:
            return HttpResponse('404 Error! Not found: ' + request.GET.get("id"))

    elif request.GET.get("item") == "ebs":

        content1['thead'] = []
        table_name = 'aws.development_Elastic_Beanstalk'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "s3":

        content1['thead'] = []
        table_name = 'aws.development_S3'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "iam":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_iam_users'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    else:
        raise Http404()

def get_legacy_data(request):
    content1 = {}
    content1['env'] = 'legacy'
    cursor = connection.cursor()

    domain_dict = {}

    #首先把zone_name和zone_id的表解析一下
    for i in connection.introspection.get_table_list(cursor):
        if "_zone_" in i.name.lower() and '_id_' in i.name.lower() and content1['env'] in i.name.lower():

            zone_id = re.split(r"\[|\]", i.name)[3].encode('utf8')
            zone_name = re.split(r"\[|\]", i.name)[1].encode('utf8')
            domain_dict[zone_id] = zone_name  # 注意,可能会有重复的zone_name, 所以zone_name不能作为key
    content1['list'] = domain_dict            # 这里domain_dict的格式为{"zone_id1": "zone_name1", "zone_id2": "zone_name2", "zone_id3":"zone_name3"}


    if request.GET.get("item") == "ec2" or not request.GET.get("item"):    #缺省显示EC2的数据

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_ec2_Instances'    #table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))    #.encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)
        return render(request, 'table.html', content1)



    elif request.GET.get("item") == "route53":
        if request.GET.get("id") in content1['list'].keys():
            zone_id = request.GET.get("id")
            zone_name = content1['list'][zone_id]

            table_name = 'aws.'+ content1['env'] + '_Zone_['+ zone_name +']_Id_[' + zone_id + ']'
            content1['thead'] = []
            for i in connection.introspection.get_table_description(cursor, table_name):
                content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
            cursor.execute("select * from `" + table_name + "`")
            content1['tbody'] = []
            for each_entry in cursor.fetchall():
                dict = {}
                for each_value in each_entry:
                    dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
                content1['tbody'].append(dict)
            return render(request, 'table.html', content1)
        if not request.GET.get("id"):
            return HttpResponse('404 Error! Usage: ?item=route53&id=[zone_id]')
        else:
            return HttpResponse('404 Error! Not found: ' + request.GET.get("id"))

    elif request.GET.get("item") == "ebs":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_Elastic_Beanstalk'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "s3":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_S3'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "iam":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_iam_users'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)
    else:
        raise Http404()

def get_staging_data(request):
    content1 = {}
    content1['env'] = 'staging'
    cursor = connection.cursor()

    domain_dict = {}

    #首先把zone_name和zone_id的表解析一下
    for i in connection.introspection.get_table_list(cursor):
        if "_zone_" in i.name.lower() and '_id_' in i.name.lower() and content1['env'] in i.name.lower():

            zone_id = re.split(r"\[|\]", i.name)[3].encode('utf8')
            zone_name = re.split(r"\[|\]", i.name)[1].encode('utf8')
            domain_dict[zone_id] = zone_name  # 注意,可能会有重复的zone_name, 所以zone_name不能作为key
    content1['list'] = domain_dict            # 这里domain_dict的格式为{"zone_id1": "zone_name1", "zone_id2": "zone_name2", "zone_id3":"zone_name3"}


    if request.GET.get("item") == "ec2" or not request.GET.get("item"):    #缺省显示EC2的数据

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_ec2_Instances'    #table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))    #.encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)
        return render(request, 'table.html', content1)



    elif request.GET.get("item") == "route53":
        if request.GET.get("id") in content1['list'].keys():
            zone_id = request.GET.get("id")
            zone_name = content1['list'][zone_id]

            table_name = 'aws.'+ content1['env'] + '_Zone_['+ zone_name +']_Id_[' + zone_id + ']'
            content1['thead'] = []
            for i in connection.introspection.get_table_description(cursor, table_name):
                content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
            cursor.execute("select * from `" + table_name + "`")
            content1['tbody'] = []
            for each_entry in cursor.fetchall():
                dict = {}
                for each_value in each_entry:
                    dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
                content1['tbody'].append(dict)
            return render(request, 'table.html', content1)
        if not request.GET.get("id"):
            return HttpResponse('404 Error! Usage: ?item=route53&id=[zone_id]')
        else:
            return HttpResponse('404 Error! Not found: ' + request.GET.get("id"))

    elif request.GET.get("item") == "ebs":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_Elastic_Beanstalk'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "s3":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_S3'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)

    elif request.GET.get("item") == "iam":

        content1['thead'] = []
        table_name = 'aws.'+ content1['env'] + '_iam_users'  # table_name
        for i in connection.introspection.get_table_description(cursor, table_name):
            content1['thead'].append(i.name.encode('utf8'))  # .encode('utf8')是去掉列表每个元素前的u
        cursor.execute("select * from `" + table_name + "`")
        content1['tbody'] = []
        for each_entry in cursor.fetchall():
            dict = {}
            for each_value in each_entry:
                dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
            content1['tbody'].append(dict)

        return render(request, 'table.html', content1)
    else:
        raise Http404()


def get_domain_info(request):
    content1 = {}
    content1['env'] = 'domain'
    cursor = connection.cursor()

    content1['thead'] = []
    table_name = 'domain_info'    #table_name
    for i in connection.introspection.get_table_description(cursor, table_name):
        content1['thead'].append(i.name.encode('utf8'))    #.encode('utf8')是去掉列表每个元素前的u
    cursor.execute("select * from `" + table_name + "`")
    content1['tbody'] = []
    for each_entry in cursor.fetchall():
        dict = {}
        for each_value in each_entry:
            dict[content1['thead'][each_entry.index(each_value)]] = str(each_value).encode('utf8')
        content1['tbody'].append(dict)
    return render(request, 'table.html', content1)
