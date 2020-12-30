import json
import logging
import re
from urllib.parse import urlencode

import scrapy
from scrapy.utils.log import configure_logging

configure_logging(settings=None, install_root_handler=False)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    level=logging.INFO,
    filename='logs.txt'
)
logger = logging.getLogger('test_scrape_logger')


# Only uncomment the commented lines in this function
# if intend to test with Crawlera's proxy.
def get_url(url):
    api = "d435634462841ff4b7c8532fb8290201"
    # payload = {'api_key': api, 'url': url}
    # proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    # return proxy_url
    return url


class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    def start_requests(self):

        json_path = '../legacy_ranking_list.json'
        with open(json_path, 'r') as file:
            content = json.load(file)

        for index, query in enumerate(content[0:5]):
            logger.info(f'Currently scraping {query} at number {index}...')
            url = 'https://www.amazon.de/s?' + urlencode({'k': query})
            yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response, meta={'keyword': query})

    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')[0:10]

        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.de/dp/{asin}"
            yield scrapy.Request(url=get_url(product_url), callback=self.parse_product_page, meta={'asin': asin, 'keyword': response.meta['keyword'], 'product_url': product_url})

        # next_page = response.xpath('//li[@class="a-last"]/a/@href').extract_first()
        # if next_page:
        #     url = urljoin("https://www.amazon.com", next_page)
        #     yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_product_page(self, response):
        """
        MEHN, ITS TOUGH TO EXPLAIN ALL THIS CSS SELECTORS :)
        YOURE SMART YOURE FIGURE IT OUT.... :)
        """

        keyword = response.meta['keyword']
        asin = response.meta['asin']
        title = response.xpath('//*[@id="productTitle"]/text()').extract_first()
        image = re.search('"large":"(.*?)"', response.text).groups()[0]
        category = response.css('#nav-subnav > a.nav-a.nav-b > span::text').get().strip()

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

        yield {
            'keyword': keyword,
            'asin': asin,
            'title': title, 'image': image, 'category': category,
            'rating': rating, 'numberofreviews': number_of_reviews,
            'price': price, 'AvailableSizes': sizes, 'availablecolors': colors,
            'bulletpoints': bullet_points,
            'link': response.meta['product_url']
        }
