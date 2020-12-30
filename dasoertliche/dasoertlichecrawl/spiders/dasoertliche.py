import html
import json
import random

import scrapy


class DasoertlicheSpider(scrapy.Spider):
    name = 'dasoertliche'
    handle_httpstatus_list = [410]

    def start_requests(self):
        link = "https://www.dasoertliche.de/?zvo_ok=0&buc=2239&plz=&quarter=&district=&ciid=&kw={}" \
               "&ci=&kgs=&buab=&zbuab=&form_name=search_nat"

        json_path = '../legacy_ranking_list.json'
        with open(json_path, 'r') as file:
            content = json.load(file)

            for key in content:
                yield scrapy.Request(link.format(html.escape(key)), self.parse, meta={'keyword': key}, dont_filter=True)

    def unescape(self, data):
        return html.unescape(data).strip()

    def parse(self, response, **kwargs):
        result = response.css('div.myframex div.hit') or False
        alternative = response.css('div.greybox table tr')
        if result:
            for each in result[0:5]:
                result_link = each.css('h2 a::attr(href)').get()

                if result_link:
                    result_link = response.urljoin(result_link)
                    yield response.follow(result_link, self.parse_detail, meta={'item': each, 'keyword': response.meta['keyword']})

        if alternative:
            for each in [random.choice(alternative)]:
                alt_link = each.css('td a::attr(href)').get()
                if alt_link:
                    yield response.follow(response.urljoin(alt_link), self.parse_alt, meta={'keyword': response.meta['keyword']})

    def parse_alt(self, response, **kwargs):
        result = response.css('div.myframex div.hit')
        if result:
            for each in result[0:5]:
                result_link = each.css('h2 a::attr(href)').get()

                if result_link:
                    result_link = response.urljoin(result_link)
                    yield response.follow(result_link, self.parse_detail, meta={'item': each, 'keyword': response.meta['keyword']})

    def parse_detail(self, response):
        item = response.meta['item']
        address = f"{item.css('address::text').get().strip()} {item.css('address span::text').get().strip()}"

        yield {
            'keyword': response.meta['keyword'],
            'name': self.unescape(item.css('div.left h2 a span::text').get()),
            'address': self.unescape(address),
            'email': item.css('div.left a.hitlnk_mail::attr(href)').get(),
            'website': item.css('div.left a.hitlnk_url::attr(href)').get(),
            'telephone': response.css('div.right table tr td span::text').get()
        }