
环境准备
安装python2.7以上版本
修改server时区为当前时区,因为脚本会记录抓取时间

安装boto3及pymysql模块
pip install boto3
pip install PyMySQL

指定配置config.ini
默认会查找当前目录下的config.ini, 如果没有会报错, 也可以aws.py -c /etc/config.ini的方式指定配置文件

配置详解
aws_tag是数据表的前缀, 运行脚本以后, 会在数据库中生成等aws_tag_Instance, aws_tag_Zone_mydomain.com.等表

运行
python aws.py
or
python aws.py -c config.ini


其它说明:
1, 每张表的最后有一个MysqlRecordTime的字段, 该字段记录了该脚本的抓取时间, 可以通过比对服务器时间和该时间的差异, 判断脚本是否正常work.
2, 如果运行时提示pymysql.err.DataError: (1406, u"Data too long for column 'VolumeDict' at row 1"),解决办法为https://stackoverflow.com/questions/15949038/error-code-1406-data-too-long-for-column-mysql
