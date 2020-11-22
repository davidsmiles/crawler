import json

import scrapy


class AlibabaSpider(scrapy.Spider):

    name = 'alibaba'

    def start_requests(self):
        find_url = 'https://german.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={}'

        json_path = '../legacy_ranking_list.json'
        with open(json_path, 'r') as file:
            content = json.load(file)

        for key in content[0:5]:
            yield scrapy.Request(find_url.format(key), self.parse, meta={'keyword': key})

    def parse(self, response, **kwargs):
        results = response.css('div.organic-list div.organic-offer-wrapper') or \
                  response.css(
                      'div > div.app-organic-search__main-body > div.app-organic-search__content > div > div > div > div')
        for each in results[0:3]:
            each_url = each.css('div > div.organic-gallery-offer-section__title > h4 > a::attr(href)').get() or \
                       each.css('div.list-no-v2-main__top-area > h4 > a::attr(href)').get()
            if each_url:
                each_url = response.urljoin(each_url)
                yield response.follow(each_url, self.parse_detail, meta={'item': each, 'keyword': response.meta['keyword']})

    def parse_detail(self, response):
        desc_details = response.css('div.do-content > div.do-overview > div:nth-child(1) > div.do-entry-list dl.do-entry-item')
        pkg = response.css('div.scc-wrapper > div > div.do-content > div > div:nth-child(n-2) > div > dl')

        data_dict = {}
        if desc_details:
            for row in desc_details:
                attr = row.css('dt span::text').get().split(':')[0].strip()
                val = row.css('dd div::text').get().strip()
                data_dict[attr] = val

        pkg_dict = {}
        if pkg:
            for row in pkg[0:-1]:
                attr = row.css('dt::text').get().split(':')[0].strip()
                val = row.css('dd::text').getall()
                pkg_dict[attr] = ' '.join(val).strip()
        del(pkg_dict[''])

        categoryyy = response.css('#page-container > div.content-header > div > div > div > ol > li')
        category = []
        for each in categoryyy:
            cat = each.css('li a span::text').get().strip()
            category.append(cat)

        image_link = response.css('#J-dcv-image-trigger::attr(src)').get()
        price = response.css('div.ma-reference-price-promotion-price > div:nth-child(1) >'
                             ' span.ma-reference-price-highlight::text').get() or \
                response.css('div.ma-spec-price.ma-price-promotion > span::text').get() or \
                response.css('div.ma-price-wrap > div > span.ma-ref-price > span::text').get() or \
                response.css('div.ma-main > div.ma-price-wrap > ul > li:nth-child(1) > div > span::text').get()

        min_order = response.css('div.ma-reference-price-promotion-moq > div > span.ma-props-title::text').get() or \
                    response.css('#ladderPrice > li.ma-ladder-price-item > div.ma-quantity-range::text').get() or \
                    response.css('div.ma-price-wrap > div > span.ma-min-order::text').get() or \
                    response.css('div.ma-price-wrap > ul > li:nth-child(1) > span::text').get()

        product_data = {
            'keyword': response.meta['keyword'],
            'name': response.css('div.scc-wrapper > div > div.ma-title-wrap > h1::text').get(),
            'image_link': image_link.replace('//', '') if image_link else None,
            'category': category[2],
            'subcategory': '|'.join(category[3:]),
            'price_range': price,
            'min_order': min_order.strip() if min_order else None,
            'details': data_dict,
            'packaging_and_delivery': pkg_dict,
            'link': response.url
        }

        yield product_data
