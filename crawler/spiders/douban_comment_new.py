import scrapy
import json
import re
import redis
import logging
from tqdm import tqdm
from ..items import DoubanCommentItem
from ..custom_settings import douban_comment_settings



def wrap(dic, keyList, default = ""):
    try:
        for key in keyList:
            dic = dic[key]
        return dic
    except:
        return default


with open('/home/vipl/workspace/Crawler/crawler/new_movie_5.txt') as f:
    hh = f.readlines()
    hh = [item.split('\n')[0] for item in hh]
movie_ids_new = hh


class DoubanCommentSpider(scrapy.Spider):
    
    name = "DoubanComment_new"
    custom_settings = douban_comment_settings
    
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
        
        movie_ids = list(self.red.smembers('douban_movie_list'))
        with open('/home/vipl/workspace/Crawler/crawler/new_movie_5.txt') as f:
            hh = f.readlines()
            hh = [item.split('\n')[0] for item in hh]
        movie_ids_new = hh
        movie_ids = [str(movie_id, 'utf-8') for movie_id in movie_ids]
        for item in movie_ids_new:
            movie_ids.append(item)
        #print(self.settings)
        if "UPPER" in self.settings  and "LOWER" in self.settings:    
            upper_bound = int( len(movie_ids) * float(self.settings["UPPER"]) )
            lower_bound = int( len(movie_ids) * float(self.settings["LOWER"]) )
            movie_ids = movie_ids[lower_bound : upper_bound]
            print(f"from {lower_bound} to {upper_bound}")
        # movie_ids = ["34874432"]
        # movie_ids = movie_ids[:5]
        movie_ids.sort()
        pbar = tqdm(movie_ids)
        flag = False
        for i, movie_id in enumerate(pbar):
            movie_id = str(movie_id, 'utf-8') if type(movie_id) != str else movie_id
            if movie_id == '26826398':
                print('Continue! 26826398')
                flag = True
            if not flag:
                continue
            pbar.set_description("Crawling:")
            url = f"https://m.douban.com/rexxar/api/v2/movie/{movie_id}/interests?count=20&order_by=hot&anony=0&start=0&ck=&for_mobile=1"
            yield scrapy.Request(url = url, 
                                 callback = self.pre_parse, 
                                 priority = -1000000,
                                 meta = {
                                     'movie_id': movie_id, 
                                     'time': -i,
                                     
                                     'index_value': movie_id,
                                     'duplicate_removal': False, 
                                     'store_db': self.db,
                                     'store_key': 'seen_douban_movie_id_for_comment',
                                 })
    

    def pre_parse(self, response):
        movie_id = response.meta['movie_id']
        time = response.meta['time']
        #data = json.loads(response.body)
        try:
            data = json.loads(response.body)
            #print(data)
            #print(len(data['interests']))
            if len(data['interests']) == 0:
                #print('Here 2')
                return 
        except:
            #print('Here 3')
            return 
        
        total = wrap(data, ['total'])
        if total > 600:
            max_page = (total - 600) // 600 + 1
        else:
            print(f"time: {time}, movie: {movie_id}, total = {total} <= 600, jump!")
            max_page = 0
        for i in range(max_page):
            start = 600 * (i + 1)
            url = f"https://m.douban.com/rexxar/api/v2/movie/{movie_id}/interests?order_by=hot&start={start}"
            yield scrapy.Request(url = url, 
                     callback = self.parse, 
                     priority = time,
                     meta = {
                         'movie_id': movie_id, 
                         'time': time,
                         'start': start,
                         'duplicate_removal': False,
                     })
        
    
    def parse(self, response):
        
        movie_id = response.meta['movie_id']
        time = response.meta['time']
        start = response.meta['start']
        try:
            data = json.loads(response.body)
            if len(data['interests']) == 0:
                print(f"time: {time}, movie: {movie_id}, start: {start}, data:{data}")
                print(response.url)
                yield self._retry(response.request, ValueError, self)
                # return 
        except:
            print(f"time: {time}, movie: {movie_id}, body:{response.body}")
            yield self._retry(response.request, ValueError, self)

        total = wrap(data, ['total'])
        
        print(f"time: {time}, movie: {movie_id}, start = {start}, len = {len(data['interests'])}, total = {total}")
        
        for uData in data["interests"]:
            uItem = DoubanCommentItem()
            uItem["type"] = "doubancommentitem_new"
            uItem["movie_id"] = movie_id
            uItem["comment"] = wrap(uData, ["comment"])
            uItem["create_time"] = wrap(uData, ["create_time"])
            uItem["id"] = wrap(uData, ["id"])
            uItem["rating"] = wrap(uData, ["rating", "value"])
            uItem["recommend_reason"] = wrap(uData, ["recommend_reason"])
            uItem["sharing_url"] = wrap(uData, ["sharing_url"])
            uItem["user_uid"] = wrap(uData, ["user", "uid"])
            uItem["user_name"] = wrap(uData, ["user", "name"])
            uItem["vote_count"] = wrap(uData, ["vote_count"])
            test_list = uItem["create_time"].split('-')
            #print(int(test_list[0]), int(test_list[1]))
            if movie_id in movie_ids_new or (int(test_list[0]) >= 2022 and int(test_list[1]) >= 7):
                print(f'Update: ', movie_id)
                yield uItem 