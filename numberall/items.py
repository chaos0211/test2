# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NumberallItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HuxingItem(scrapy.Item):
    detail_url = scrapy.Field()
    building_name = scrapy.Field()
    building_url = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    area = scrapy.Field()
    oss_url = scrapy.Field()
    price = scrapy.Field()
    config_id = scrapy.Field()
    desc_text = scrapy.Field()
    img_url = scrapy.Field()
    hx_url = scrapy.Field()
    pj_name = scrapy.Field()
    city = scrapy.Field()

class TupianItem(scrapy.Item):
    building_name = scrapy.Field()
    building_url = scrapy.Field()
    pic_label = scrapy.Field()
    oss_urls = scrapy.Field()
    city = scrapy.Field()
    pj_name = scrapy.Field()
    city = scrapy.Field()


class DongtaiItem(scrapy.Item):
    pj_name = scrapy.Field()
    trend_title = scrapy.Field()
    trend_date = scrapy.Field()
    trend_contents = scrapy.Field()
    city = scrapy.Field()
