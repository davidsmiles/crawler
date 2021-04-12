# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import pymongo
from itemadapter import ItemAdapter


class EbaycrawlPipeline:
    """
        Uncomment this code if you want the crawler to write to mongodb instead
        Replace URL with connection uri of your mongodb database
        """

    def __init__(self):
        url = f"mongodb://seoadmin:GOOGLEPLSRANKME%21%21%21@202.61.242.18:27017/crawler?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
        self.client = pymongo.MongoClient(url)
        db = self.client['crawler']
        self.ebay = db.ebay
        self.ebaykeywords = db.ebaykeywords

    def process_item(self, item, spider):
        """
            UNCOMMENT LINE TO ALLOW INSERTION INTO THE MONGODB DATABASE
        """
        keyword = item['keyword']
        query = {"keyword": keyword}
        value = {"$set": {"crawled": "Done"}}

        self.ebaykeywords.update_one(query, value)
        self.ebay.insert(dict(item))
        return item
