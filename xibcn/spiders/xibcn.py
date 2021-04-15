import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from xibcn.items import Article


class xibcnSpider(scrapy.Spider):
    name = 'xibcn'
    start_urls = ['https://www.xib.com.cn/bfth/index.htm#']

    def parse(self, response):
        articles = response.xpath('//li[span]')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./span/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="pageDetailbox"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
