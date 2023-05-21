# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors
from rich import print

from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings


class CrawlerPipeline:
    def process_item(self, item, spider):
        return item


class CrawlerTwistedPipeline(object):
    
    def __init__(self):
        settings = get_project_settings()
        dbparams = {
            'host'       : settings.get('MYSQL_HOST'),
            'port'       : settings.get('MYSQL_PORT'),
            'user'       : settings.get('MYSQL_USER'),
            'password'   : settings.get('MYSQL_PASSWORD'),
            'database'   : settings.get('MYSQL_DBNAME'),
            'charset'    : 'utf8mb4',
            'cursorclass': cursors.DictCursor,
        }
        self.dbpool = adbapi.ConnectionPool('pymysql',**dbparams)



    def process_item(self, item, spider):
        defer = self.dbpool.runInteraction(self.insert_item, item) 
        defer.addErrback(self.handle_error, item, spider) 
        return item
        
    
    def insert_item(self, cursor, item):

        table_name = item['type']
        fields = list(item.fields.keys())
        field_sql = ",".join(fields)
        value_sql = ",".join(["%s"] * len(fields))
        sql = f"insert into {table_name}({field_sql}) VALUES({value_sql})"
        values = list(item[field] for field in fields)
        cursor.execute(sql, values)

    
    
    def handle_error(self, error, item, spider):
        print('='*20+'error'+'='*20)
        print(error)
        print('='*20+'error'+'='*20)