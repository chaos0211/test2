# -*- coding: utf-8 -*-
import scrapy
from ..items import HuxingItem,TupianItem,DongtaiItem
import datetime
import requests
import oss2
import re
import copy
import json

class ZongheSpider(scrapy.Spider):
    name = 'zonghe'
    allowed_domains = ['anjuke.com']
    # start_urls = ['https://hefei.fang.anjuke.com/loupan/all/p{}/']
    start_urls = ['https://nanchang.fang.anjuke.com/loupan/?from=navigation']
    # city_list = ['hefei', 'hangzhou','tianjin', 'wuhan', 'chengdu', 'jinan', 'changsha', 'zhengzhou', 'nanjing',
    #     #                  'xuzhou', 'guiyang', 'nanning', 'chongqing', 'nanchang']

    auth = oss2.Auth('LTAIfmphqi2EbxOH', 'kWHBkKWfb81cZdP1bdUeUNaxtsbE9y')
    # bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'test-yigongtech')
    bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', 'yigongfangchan')
    date_tody = str(datetime.date.today()).replace('-', '')

    def parse(self, response):
        div_list = response.xpath("//div[@class='key-list']/div")
        for div in div_list:
            building_url = div.xpath("./div/a/@href").extract_first()
            # print(detail_url)
            yield scrapy.Request(
                url=building_url,
                callback=self.parse_mainpage,
            )
        next_url = response.xpath("//a[text()='下一页']/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(
                url = next_url,
                callback=self.parse,
            )

    def parse_mainpage(self, response):
        lei_list= response.xpath("//ul[@class='lp-navtabs clearfix']/li/a/text()").extract()
        for lei in lei_list:
            url = response.xpath("//a[text()='%s']/@href" % lei).extract_first()
            # print(url)
            if lei == '  户型':
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_huxing
                )

            elif lei == '  相册':
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_tupian
                )
            elif lei == '  动态资讯':
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_dongtai
                )

    def parse_huxing(self, response):
        item = HuxingItem()
        ul_list = response.xpath("//ul[@class='hx-list g-clear']/li")
        for ul in ul_list:
            item['url'] = ul.xpath("./a/@href").extract_first()
            # print(item)
            yield scrapy.Request(
                url=item['url'],
                callback=self.parse_huxing_detail,
                meta={"item": copy.deepcopy(item)}
            )

        next_url = response.xpath("//div[@class='pagination']/a[@class='next-page next-link']/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_huxing,
            )

    def parse_huxing_detail(self, response):
        item = response.meta['item']
        name = response.xpath("//div[@class='hx-de-right']/h3/span/text()").extract_first()
        if name is not None:
            name = name.replace(' ', '').split('，')
            item['name'] = name[0].replace('\n', '') + " " + name[1]
            item['area'] = name[2]
            item['area'] = re.findall(r'\d+\.?\d*', item['area'])[0]
            try:
                item['area'] = item['area'].replace('.00', '')
            except:
                pass

        desc = response.xpath("//div[@class='hx-des-wrap']/p/span/text()").extract()
        item['desc_text'] = ''.join(desc)
        item['price'] = response.xpath("//span[@class='total-price t-price-wrap']/text()").extract_first()
        if item['price'] is not None:
            item['price'] = item['price'].replace('万元/套', '')
        else:
            item['price'] = 0
        item['pj_name'] = response.xpath("//div[@class='lp-tit']/h1/text()").extract_first()
        item['city'] = response.xpath("//div[@class='crumb-item fl']/a[1]/text()").extract_first()
        if item['city'] is not None:
            item['city'] = item['city'][0] + item['city'][1] + '%'
        img_url = response.xpath("//li[@class='item pic-item']/img/@imglazyload-src").extract_first().replace(
            '.jpg', 'a.jpg')

        # auth = oss2.Auth('LTAIfmphqi2EbxOH', 'kWHBkKWfb81cZdP1bdUeUNaxtsbE9y')
        # # bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'test-yigongtech')
        # bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', 'yigongfangchan')
        #
        image_name = img_url.split('/')[-2]
        input1 = requests.get(img_url)
        self.bucket.put_object(self.date_tody + '/' + image_name + '.jpg', input1)
        # # TODO 以上代码已顺利传送图片进oss服务器.需要用上传入相应的"小区:oss链接"进数据库

        oss_u = "http://img.df-house.com/"
        item['oss_url'] = oss_u + self.date_tody + '/' + img_url.split('/')[-2] + ".jpg"

        print('图片上传完毕', datetime.datetime.now())
        print(item)
        yield item

    def parse_tupian(self, response):
        item = TupianItem()
        text_list = response.xpath("//div[@class='album-head']/a/text()")
        item['pj_name'] = response.xpath("//div[@class='lp-tit']/h1/text()").extract_first()
        item['city'] = response.xpath("//div[@class='crumb-item fl']/a[1]/text()").extract_first()
        if item['city'] is not None:
            item['city'] = item['city'][0] + item['city'][1] + '%'
        for text in text_list.extract():
            url = response.xpath("//a[text()='%s']/@href" % text).extract_first()
            if text == '实景图':
                # print(url)
                item['pic_label'] = '10'
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_tupian_detail,
                    meta={"item": copy.deepcopy(item)}
                )

            elif text == '交通图':
                item['pic_label'] = '11'
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_tupian_detail,
                    meta={"item": copy.deepcopy(item)}
                )

            elif text == '效果图':
                item['pic_label'] = '1'
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_tupian_detail,
                    meta={"item": copy.deepcopy(item)}
                )
            elif text == '配套图':
                item['pic_label'] = '4'
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_tupian_detail,
                    meta={"item": copy.deepcopy(item)}
                )
            elif text == '规划图':
                item['pic_label'] = '5'
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_tupian_detail,
                    meta={"item": copy.deepcopy(item)}
                )

    def parse_tupian_detail(self, response):
        item = response.meta['item']
        ul_list = response.xpath("//ul[@class='others-b xiangce-list clearfix']/li")
        item1 = []
        for ul in ul_list:
            pic_src = ul.xpath("./a/img/@imglazyload-src").extract_first()
            # print(pic_src)

            # auth = oss2.Auth('LTAIfmphqi2EbxOH', 'kWHBkKWfb81cZdP1bdUeUNaxtsbE9y')
            # bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'test-yigongtech')
            # bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', 'yigongfangchan')
            # #
            image_name = pic_src.split('/')[-2]
            input1 = requests.get(pic_src)
            # self.bucket.put_object('20180703/' + image_name + '.jpg', input1)
            self.bucket.put_object(self.date_tody + '/' + image_name + '.jpg', input1)
            # # TODO 以上代码已顺利传送图片进oss服务器.需要用上传入相应的"小区:oss链接"进数据库

            oss_u = "http://img.df-house.com/"
            # image = oss_u + pic_src.split('/')[-2] + ".jpg"
            image = oss_u + self.date_tody + '/' + pic_src.split('/')[-2] + ".jpg"

            item1.append(image)

        print('图片上传完毕', datetime.datetime.now())
        item['oss_urls'] = json.dumps(item1)
        print(item)
        yield item

    def parse_dongtai(self, response):
        div_list = response.xpath("//div[@id='all_hidden']/div/@link").extract()
        for div in div_list:
            yield scrapy.Request(
                url=div,
                callback=self.parse_dongtai_detail
            )

    def parse_dongtai_detail(self, response):
        item = DongtaiItem()
        item['city'] = response.xpath("//div[@class='crumb-item fl']/a[1]/text()").extract_first()
        if item['city'] is not None:
            item['city'] = item['city'][0] + item['city'][1] + '%'
        item['pj_name'] = response.xpath("//div[@class='lp-links']/span/text()").extract_first()
        item['trend_title'] = response.xpath("//div[@class='news-detail']/h1/text()").extract_first()
        item['trend_date'] = response.xpath("//div[@class='tit-sub gray']/span/text()").extract_first()
        if item['trend_date'] is not None:
            item['trend_date'] = item['trend_date'].replace('年', '-').replace('月', '-').replace('日', '')
        b = response.xpath("//div[@class='news-detail']/div[@class='infos']/p/text()").extract()
        item['trend_contents'] = []
        for a in b:
            if item['trend_contents'] is not None:
                item['trend_contents'].append(a.replace('\r', '').replace('\t', '').replace('\n', '').replace('\u3000', ''))
        item['trend_contents'] = ''.join(item['trend_contents'])
        print(item)
        yield item