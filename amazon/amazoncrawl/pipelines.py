# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import pymongo
from itemadapter import ItemAdapter


class AmazoncrawlPipeline:

    """
    Uncomment this code if you want the crawler to write to mongodb instead
    Replace URL with connection uri of your mongodb database
    """
    # def __init__(self):
    #     URL = "<link to mongodb database>"
    #     self.client = pymongo.MongoClient(URL)
    #     db = self.client['<set-name-of-database eg. scraped-data>']  # set name of database
    #     self.collection = db['<set-name-of-collection eg. amazon>']    # set name of collection

    def process_item(self, item, spider):
        for k, v in item.items():
            if not v:
                item[k] = ''  # replace empty list or None with empty string
                continue
            if k == 'title':
                item[k] = v.strip()
            elif k == 'rating':
                item[k] = v.replace(' out of 5 stars', '')
            elif k == 'availablesizes' or k == 'availablecolors':
                item[k] = ", ".join(v)
            elif k == 'bulletpoints':
                item[k] = ", ".join([i.strip() for i in v if i.strip()])


        """
            UNCOMMENT LINE TO ALLOW INSERTION INTO THE MONGODB DATABASE
        """
        # self.collection.insert(dict(item))
        return item