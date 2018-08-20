# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .items import HuxingItem,TupianItem,DongtaiItem
import pymysql
import time

class NumberallPipeline(object):
    def open_spider(self, spider):
        self.connect = pymysql.connect(host='rm-uf65163t7ka9v01q0o.mysql.rds.aliyuncs.com',
                                       port=3306,
                                       database='yigong_db',
                                       user='dingfang',
                                       password='bNk6izHcGVWSTOtCGJXP',
                                       charset='utf8')
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if isinstance(item, HuxingItem):
            self.cursor.execute(
                ''' select city_id from city where name LIKE %s ''', item['city']
            )
            city = self.cursor.fetchone()

            self.cursor.execute(
                ''' select id from python_project where pj_name = %s and city_id=%s and building_from=3''',(item['pj_name'], city)
            )
            building_id = self.cursor.fetchone()
            # print(building_id)

            self.cursor.execute(
                '''select id from python_huxing where building_id = %s and name = %s''',(building_id, item['name'])
            )
            id = self.cursor.fetchone()
            print('这是楼盘id:', building_id)
            print('这是户型id:', id)

            if building_id is not None:
                try:
                    self.cursor.execute(
                        '''replace into
                            python_huxing(id,building_id, name, url, area, oss_url, price, desc_text)
                            values (%s,%s,%s,%s,%s,%s,%s,%s)''',
                        (
                            id,
                            building_id,
                            item['name'],
                            item['url'],
                            item['area'],
                            item['oss_url'],
                            item['price'],
                            item['desc_text']
                        )
                    )
                    self.connect.commit()
                except:
                    pass
                print('*' * 100)

        if isinstance(item, TupianItem):

            time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            self.cursor.execute(
                ''' select city_id from city where name LIKE %s ''', item['city']
            )
            city = self.cursor.fetchone()

            self.cursor.execute(
                ''' select id from python_project where pj_name = %s and city_id=%s and building_from=3''', (item['pj_name'], city)
            )
            building_id = self.cursor.fetchone()

            self.cursor.execute(
                '''select id from python_xiangche where building_id = %s and pic_label = %s''',(building_id, item['pic_label'])
            )
            id = self.cursor.fetchone()
            print('这是楼盘id:', building_id)
            print('这是相册id:',id)

            if building_id is not None:
                try:
                    self.cursor.execute(
                        '''replace into
                            python_xiangche(id,building_id, pic_label, oss_urls, commit_time, target)
                            values (%s,%s,%s,%s,%s,'0')''',
                        (
                            id,
                            building_id,
                            item['pic_label'],
                            item['oss_urls'],
                            time_now,
                        )
                    )
                    self.connect.commit()
                except:
                    pass
                print('*' * 100)

        if isinstance(item, DongtaiItem):
            self.cursor.execute(
                ''' select city_id from city where name LIKE %s ''', item['city']
            )
            city = self.cursor.fetchone()

            self.cursor.execute(
                ''' select id from python_project where pj_name = %s and city_id=%s and building_from=3''', (item['pj_name'], city)
            )
            building_id = self.cursor.fetchone()

            time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print(time_now)
            self.cursor.execute(
                '''select id from python_building_trend where building_id = %s and trend_date = %s''', (building_id, item['trend_date'])
            )
            id = self.cursor.fetchone()
            print('这是楼盘id:', building_id)
            print('这是动态资讯id:', id)
            # print(time_now)
            if building_id is not None:
                self.cursor.execute(
                    '''replace into
                        python_building_trend(id,building_id, trend_title, trend_date, trend_contents, commit_time)
                        values (%s,%s,%s,%s,%s,%s)''',
                    (
                        id,
                        building_id,
                        item['trend_title'],
                        item['trend_date'],
                        item['trend_contents'],
                        time_now,
                    )
                )
                self.connect.commit()
            print('*' * 100)


    def close_spider(self, spider):
        # 关闭
        self.cursor.close()

        self.connect.close()
        # 打印done表示完成
        print("done!!!")
