import scrapy
import json
import re
import redis
import logging
from tqdm import tqdm
from ..items import DoubanMovieListItem
from ..custom_settings import douban_movielist_settings
import sys



def wrap(dic, keyList, default = ""):
    try:
        for key in keyList:
            dic = dic[key]
        return dic
    except:
        return default


class DoubanMovieListSpider(scrapy.Spider):
    
    name = "DoubanMovieList"
    custom_settings = douban_movielist_settings
    
    def __init__(self, settings, *args, **kwargs):
        
        super().__init__()
        self.settings = settings
        self.allowed_domains = ["douban.com"]
        self.db = 0
        self.red = redis.Redis(host = settings.get('REDIS_HOST'), 
                               port = settings.get('REDIS_PORT'), 
                               password = settings.get('REDIS_PASSWORD'),
                               db = self.db, decode_responses=True) 
        self.movie_ids = list(self.red.smembers('douban_movie_list'))
        print(len(self.movie_ids))
        self.new_list = []
        self.start_year = 2012
        self.end_year = 2022
        self.count = 0

        if "S" in self.settings  and "E" in self.settings:    
            self.start_year = self.settings['S']
            self.end_year = self.settings['E']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider


    def start_requests(self):
        print("Start crawling...")
        # user_ids = ["62381482"]
        
        base = 20
        # for i in tqdm(range(self.start_year, self.end_year + 1)):
        for j in range(32000):
            print(j)
            url = f"https://movie.douban.com/j/new_search_subjects?sort=R&tags=%E7%94%B5%E5%BD%B1&start={j*20}&year_range={self.start_year},{self.end_year}"
            yield scrapy.Request(url = url, 
                                 callback = self.parse,
                                 meta = {
                                     'year': [self.start_year, self.end_year],
                                     'page': j * 20,
                                     'duplicate_removal': False,
                                 })
    
    def parse(self, response):
        year = response.meta['year']
        page = response.meta['page']
        try:
            data = json.loads(response.body)
            if len(data['data']) == 0:
                return 
        except:
            print(response.body)
            return 
            # url = f"https://movie.douban.com/j/new_search_subjects?sort=R&tags=%E7%94%B5%E5%BD%B1&start={page}&year_range={year},{year}"
            # return scrapy.Request(url = url, callback = lambda response, year = year, page = page: self.parse(response, year, page))
        for movie in data['data']:
            self.count += 1
            # status = self.red.sadd('douban_movie_id_list', movie['id'])
            print(self.count, year, page, movie['title'], movie['id'])
            if movie['id'] not in self.movie_ids and (movie['id'] not in self.new_list):
                self.new_list.append(movie['id'])
            
                print(f'NEWWWWW!: ', movie['id'], len(self.new_list))
        
                file=open('new_movie_5.txt','a') 
                file.write(movie['id'] + '\n')
                file.close()
                #exit()
        
            # item = DoubanMovieListItem()
            # item["type"]        = "doubanmovielistitem"
            # item["directors"]   = wrap(movie, ['directors'])
            # item["rate"]        = wrap(movie, ['rate'])
            # item["star"]        = wrap(movie, ['star'])
            # item["cover_x"]     = wrap(movie, ['cover_x'])
            # item["title"]       = wrap(movie, ['title'])
            # item["year"]        = year
            # item["url"]         = wrap(movie, ['url'])
            # item["casts"]       = wrap(movie, ['casts'])
            # item["cover"]       = wrap(movie, ['cover'])
            # item["id"]          = wrap(movie, ['id'])
            # item["cover_y"]     = wrap(movie, ['cover_y'])
            # yield item
