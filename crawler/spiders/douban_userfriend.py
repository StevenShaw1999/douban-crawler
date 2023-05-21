import scrapy
import json
import re
import redis
import logging
from tqdm import tqdm
from ..items import DoubanUserFriendItem
from ..custom_settings import douban_friend_settings



def wrap(dic, keyList, default = ""):
    try:
        for key in keyList:
            dic = dic[key]
        return dic
    except:
        return default


class DoubanUserFriendSpider(scrapy.Spider):
    
    name = "DoubanUserFriend"
    custom_settings = douban_friend_settings
    
    def __init__(self, settings, *args, **kwargs):
        
        super().__init__()
        self.settings = settings
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
        # user_ids = ["62381482"]
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
            yield scrapy.Request(url = f"https://m.douban.com/rexxar/api/v2/user/{user_id}/following?start=0&count=10000&ck=YTlm&for_mobile=1", 
                                 callback = self.parse, 
                                 priority = 10,
                                 meta = {
                                     'user_id': user_id, 
                                     
                                     'index_value': user_id,
                                     'duplicate_removal': True,
                                     'store_db': self.db,
                                     'store_key': 'seen_user_id_for_friend',
                                 })
    

    def parse(self, response):
        user_id = response.meta['user_id']
        try:
            data = json.loads(response.body)
            if len(data['users']) == 0:
                return 
        except:
            return 
            # logging.error(response, response.body)
        
        for uData in data["users"]:
            uItem = DoubanUserFriendItem()
            uItem["type"] = "doubanuserfrienditem"
            uItem["user_id"] = user_id
            uItem["friend_id"] = wrap(uData, ["id"])
            uItem["friend_uid"] = wrap(uData, ["uid"])
            uItem["friend_name"] = wrap(uData, ["name"])
            uItem["friend_avatar"] = wrap(uData, ["avatar"])
            yield uItem 