import scrapy
import json
import redis
import logging
from tqdm import tqdm
from ..items import DoubanUserGuangboItem

def wrap(dic, keyList, default = ""):
    try:
        for key in keyList:
            dic = dic[key]
        return dic
    except:
        return default


class DoubanUserGuangboSpider(scrapy.Spider):

    name = "DoubanUserGuangbo"

    def __init__(self, settings, *args, **kwargs):
        super().__init__()
        self.allowed_domains = ["douban.com"]
        self.db = 0
        self.red = redis.Redis(host = settings.get('REDIS_HOST'), 
                               port = settings.get('REDIS_PORT'), 
                               password = settings.get('REDIS_PASSWORD'),
                               db = self.db) 


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider
    
    
    def start_requests(self):
        print("Start crawling...")
        # user_ids = ["100006093"]
        user_ids = list(self.red.smembers('user_list'))
        user_ids.sort()
        
        if "UPPER" in self.settings  and "LOWER" in self.settings:    
            upper_bound = int( len(user_ids) * float(self.settings["UPPER"]) )
            lower_bound = int( len(user_ids) * float(self.settings["LOWER"]) )
            user_ids = user_ids[lower_bound : upper_bound]

        pbar = tqdm(user_ids)
        for i, user_id in enumerate(pbar):
            user_id = str(user_id, 'utf-8') if type(user_id) != str else user_id
            pbar.set_description("Crawling:")
            yield scrapy.Request(url = f"https://m.douban.com/rexxar/api/v2/status/user_timeline/{user_id}?max_id=&ck=YTlm&for_mobile=1",
                                 callback = self.parse, 
                                 priority = 10,
                                 meta = {
                                     'user_id': user_id, 
                                     'cnt': 0, 
                                     'index_value': user_id,
                                     'duplicate_removal': True,
                                     'store_db': self.db,
                                     'store_key': 'seen_user_id_for_guangbo',
                                 })
    

    def parse(self, response):
        
        # import ipdb; ipdb.set_trace()
        user_id = response.meta['user_id']
        cnt = response.meta['cnt']
        
        try:
            data = json.loads(response.body)
            if len(data['items']) == 0:
                return 
        except:
            print(response.body)
            return 


        for uData in data["items"]:
            
            uItem = DoubanUserGuangboItem()
            uItem["type"]        = "DoubanUserGuangboItem"
            uItem["id"]          = wrap(uData, ["status", "id"])
            uItem["activity"]    = wrap(uData, ["status", "activity"])
            uItem["author_id"]   = wrap(uData, ["status", "author", "id"])
            uItem["author_uid"]  = wrap(uData, ["status", "author", "uid"])
            uItem["create_time"] = wrap(uData, ["status", "create_time"])
            uItem["text"]        = wrap(uData, ["status", "text"])
            uItem["uri"]         = wrap(uData, ["status", "uri"])
            uItem["sharing_url"] = wrap(uData, ["status", "sharing_url"])
            uItem["ref"]         = "root"
            uItem["card"]        = json.dumps(wrap(uData, ["status", "card"]))
            yield uItem


            for uComment in uData["comments"]:
                cItem = DoubanUserGuangboItem()
                cItem["type"]        = "DoubanUserGuangboItem"
                cItem["id"]          = wrap(uComment, ["id"])
                cItem["activity"]    = ""
                cItem["author_id"]   = wrap(uComment, ["author", "id"])
                cItem["author_uid"]  = wrap(uComment, ["author", "uid"])
                cItem["create_time"] = wrap(uComment, ["create_time"])
                cItem["text"]        = wrap(uComment, ["text"])
                cItem["uri"]         = wrap(uComment, ["uri"])
                cItem["sharing_url"] = ""
                cItem["ref"]         = wrap(uData, ["status", "id"])
                cItem["card"]        = json.dumps(wrap(uComment, ["card"]))
                yield cItem


        # max_id = data['items'][-1]['status']['id']
        # yield scrapy.Request(url = f"https://m.douban.com/rexxar/api/v2/status/user_timeline/{user_id}?max_id={max_id}&ck=YTlm&for_mobile=1",
        #                      callback = self.parse, 
        #                      priority = 10,
        #                      meta = {
        #                          'user_id': user_id, 
        #                          'cnt': cnt + 1, 
        #                      })