# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import time
import redis
import hashlib

from scrapy import signals
from rich import print
from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.retry import RetryMiddleware as BaseRetryMiddleware

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class CrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.



        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        



class CrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s


    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        
        
        if "duplicate_removal" in request.meta: 
            if request.meta["duplicate_removal"]:
                settings = spider.settings 
                index_value = request.meta["index_value"]
                store_key = request.meta['store_key']
                store_db = request.meta['store_db']
                if store_db not in self.red_dbs:
                    self.red_dbs[store_db] = redis.Redis(host = settings.get('REDIS_HOST'), 
                                                         port = settings.get('REDIS_PORT'), 
                                                         password = settings.get('REDIS_PASSWORD'),
                                                         db = store_db) 
                if self.red_dbs[store_db].sismember(store_key, index_value):
                    raise IgnoreRequest(f"Duplicate index: {index_value}, ignore!")
                # self.red_dbs[store_db].sadd(store_key, index_value)
                
        proxy   = self.proxy
        headers = self.proxy_headers
        request.headers['Referer']             = "https://m.douban.com/movie/subject/35505100/"
        request.headers['User-Agent']          = headers['User-Agent']
        request.headers['Proxy-Authorization'] = headers['Proxy-Authorization']
        request.meta   ['proxies']             = proxy
        request.meta   ['proxy']               = proxy['https']
        return None


    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        
        if response.status == 200 and "duplicate_removal" in request.meta: 
            if request.meta["duplicate_removal"]:
                settings = spider.settings 
                index_value = request.meta["index_value"]
                store_key = request.meta['store_key']
                store_db = request.meta['store_db']
                if store_db not in self.red_dbs:
                    self.red_dbs[store_db] = redis.Redis(host = settings.get('REDIS_HOST'), 
                                                         port = settings.get('REDIS_PORT'), 
                                                         password = settings.get('REDIS_PASSWORD'),
                                                         db = store_db) 
                self.red_dbs[store_db].sadd(store_key, index_value)
        return response


    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # print(exception)
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

        timestamp = str(int(time.time()))
        orderno = spider.settings['XDAILI_ORDERNO']
        secret  = spider.settings['XDAILI_SECRET']
        string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
        string = string.encode()
        md5_string = hashlib.md5(string).hexdigest()
        sign = md5_string.upper()
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp
        agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1"
        headers = {"Proxy-Authorization": auth, "User-Agent": agent}

        ip = 'forward.xdaili.cn'
        port = "80"
        ip_port = ip + ':' + port
        proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}

        self.proxy = proxy
        self.proxy_headers = headers
        print("加载讯代理 headers")
        
        self.red_dbs = {}





class RetryMiddleware(BaseRetryMiddleware):


    def process_response(self, request, response, spider):
        # inject retry method so request could be retried by some conditions
        # from spider itself even on 200 responses
        if not hasattr(spider, '_retry'):
            spider._retry = self._retry
        return super(RetryMiddleware, self).process_response(request, response, spider)