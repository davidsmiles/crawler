import html
import json

import scrapy


class EbaycrawlSpider(scrapy.Spider):

    name = 'ebay'

    def start_requests(self):
        find_url = 'https://www.ebay.de/sch/i.html?_nkw={}'

        json_path = '../legacy_ranking_list.json'
        with open(json_path, 'r') as file:
            content = json.load(file)

        for key in content[1:2]:
            yield scrapy.Request(find_url.format(html.escape(key)), self.parse, meta={'keyword': key}, dont_filter=True)

    def parse(self, response, **kwargs):
        results = response.css('ul.srp-results li.s-item')
        for each in results[0:3]:
            each_url = each.css('div > div.s-item__info > a::attr(href)').get()

            if each_url:
                each_url = response.urljoin(each_url)
                yield response.follow(each_url, self.parse_detail, meta={'keyword': response.meta['keyword'], 'each': each})

    def parse_detail(self, response):
        item_no = response.css('#descItemNumber::text').get()
        category = []
        for each in response.css('#vi-VR-brumb-lnkLst > table > tr > td > ul > li'):
            cat = each.css('a span::text').get()
            if cat:
                category.append(cat)

        desc = response.css('div.section table tr')
        desc_link = response.css('#desc_ifr::attr(src)').get()

        list_a = []
        list_v = []
        for row in desc:
            attr = row.css('td.attrLabels::text').get()
            if attr:
                list_a.append(attr.strip().split(':')[0])
            val = row.css('td span')
            if val:
                word = []
                for each_word in val:
                    word.append(each_word.css('span::text').get().strip())
                list_v.append(''.join(word))

        desc_data = dict(zip(list_a, list_v))
        desc_data.pop('Artikelzustand', '')

        each = response.meta['each']
        # status = each.xpath('.//*[@class="SECONDARY_INFO"]/text()').extract_first()
        # seller_level = each.xpath('.//*[@class="s-item__etrs-text"]/text()').extract_first()
        # location = each.xpath('.//*[@class="s-item__location s-item__itemLocation"]/text()').extract_first()
        #
        # # Set default values
        # stars = 0
        # ratings = 0
        #
        # stars_text = each.xpath('.//*[@class="clipped"]/text()').extract_first()
        # if stars_text:
        #     stars = stars_text[:3]
        # ratings_text = each.xpath('.//*[@aria-hidden="true"]/text()').extract_first()
        # if ratings_text:
        #     ratings = ratings_text.split(' ')[0]

        product_data = {
            'keyword': response.meta['keyword'],
            'name': response.css('#itemTitle::text').get(),
            'category': category[0],
            'subcategory': '|'.join(category[1:]),
            'image': response.css('#icImg::attr(src)').get(),
            'price': response.css('#prcIsum::text').get(),
            'item_no': item_no,
            # 'status': status,
            # 'stars': stars,
            # 'rating': ratings,
            'location': each.xpath('.//*[@class="s-item__location s-item__itemLocation"]/text()').extract_first(),
            # 'seller_level': seller_level,
            'description': desc_data,
            'description_link': desc_link,
            'url': f"{response.url.split('itm')[0]}itm/{item_no}"
        }

        yield product_data
