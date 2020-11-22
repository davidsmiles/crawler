import json
import logging
import re
from urllib.parse import urlencode

import scrapy

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    level=logging.DEBUG,
    filename='logs.txt'
)
logger = logging.getLogger('test_scrape_logger')


class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    def start_requests(self):

        json_path = '../legacy_ranking_list.json'
        with open(json_path, 'r') as file:
            content = json.load(file)

        for index, query in enumerate(content):
            # logger.info(f'currently scraping {query} at number {index}')
            url = 'https://www.amazon.com/s?' + urlencode({'k': query})
            yield scrapy.Request(url=url, callback=self.parse_keyword_response, meta={'keyword': query})

    def parse_keyword_response(self, response):
        # logger.info(f'response status {response.status}')
        products = response.xpath('//*[@data-asin]')[0:10]

        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.com/dp/{asin}"
            yield scrapy.Request(url=product_url, callback=self.parse_product_page, meta={'asin': asin, 'keyword': response.meta['keyword']})

        # next_page = response.xpath('//li[@class="a-last"]/a/@href').extract_first()
        # if next_page:
        #     url = urljoin("https://www.amazon.com", next_page)
        #     yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_product_page(self, response):
        keyword = response.meta['keyword']
        asin = response.meta['asin']
        title = response.xpath('//*[@id="productTitle"]/text()').extract_first()
        image = re.search('"large":"(.*?)"', response.text).groups()[0]
        rating = response.xpath('//*[@id="acrPopover"]/@title').extract_first()
        number_of_reviews = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
        price = response.xpath('//*[@id="priceblock_ourprice"]/text()').extract_first()

        if not price:
            price = response.xpath('//*[@data-asin-price]/@data-asin-price').extract_first() or \
                    response.xpath('//*[@id="price_inside_buybox"]/text()').extract_first()

        temp = response.xpath('//*[@id="twister"]')
        sizes = []
        colors = []
        if temp:
            s = re.search('"variationValues" : ({.*})', response.text).groups()[0]
            json_acceptable = s.replace("'", "\"")
            di = json.loads(json_acceptable)
            sizes = di.get('size_name', [])
            colors = di.get('color_name', [])

        bullet_points = response.xpath('//*[@id="feature-bullets"]//li/span/text()').extract()
        seller_rank = response.xpath(
            '//*[text()="Amazon Best Sellers Rank:"]/parent::*//text()[not(parent::style)]').extract()

        yield {'keyword': keyword, 'asin': asin, 'title': title, 'image': image, 'rating': rating, 'numberofreviews': number_of_reviews,
               'price': price, 'AvailableSizes': sizes, 'availablecolors': colors, 'bulletpoints': bullet_points,
               'sellerrank': seller_rank, 'link': response.url}
