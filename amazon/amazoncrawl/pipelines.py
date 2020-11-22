# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class AmazoncrawlPipeline:
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
            elif k == 'sellerRank':
                item[k] = " ".join([i.strip() for i in v if i.strip()])
        return item