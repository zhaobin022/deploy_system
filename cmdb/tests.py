# -*- coding:utf-8 -*-
from datetime import date, datetime, timedelta
import pymysql.cursors

# 连接配置信息
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'rootroot',
    'db': 'test',
    'charset': 'utf8',
    'cursorclass': pymysql.cursors.DictCursor,
}
# 创建连接
connection = pymysql.connect(**config)

# 获取明天的时间
# tomorrow = datetime.now().date() + timedelta(days=1)

# 执行sql语句
try:
    with connection.cursor() as cursor:
        # 执行sql语句，插入记录
        for i in range(10000):
            sql = 'INSERT INTO t (id) VALUES (%s)'
            cursor.execute(sql, (i,));
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
            connection.commit()

finally:
    connection.close();