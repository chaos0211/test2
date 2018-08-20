import pymysql
from scrapy.conf import settings




class MySQLPipeline(object):
    #Connect to the MySQL database
    def __init__(self):
        self.conn =  pymysql.connect(
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            db=settings['MYSQL_DBNAME'],
            host=settings['MONGODB_SERVER'],
            charset='utf8',
            use_unicode = True
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        self.insert_news(item)
        self.conn.commit()

    def insert_news(self, item):
        args = (item['source_url'], item['news_title'], item['news_author'],
                item['news_time'], item['news_content'], item['news_source'])

        newsSqkText = '''insert into news_main("news_url", "news_title", "news_author", "news_time", "news_content", "news_resource")values (%s,%s,%s,%s,%s,%s)''' %args
        self.cursor.execute(newsSqkText)
        self.conn.commit()










