# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class DoubanMovieListItem(scrapy.Item):
    type        = scrapy.Field()
    id          = scrapy.Field()
    title       = scrapy.Field()
    year        = scrapy.Field()
    directors   = scrapy.Field()
    rate        = scrapy.Field()
    star        = scrapy.Field()
    cover_x     = scrapy.Field()
    cover_y     = scrapy.Field()
    url         = scrapy.Field()
    casts       = scrapy.Field()
    cover       = scrapy.Field()

class DoubanCommentItem(scrapy.Item):
    
    type = scrapy.Field()
    movie_id = scrapy.Field()
    comment = scrapy.Field()
    create_time = scrapy.Field()
    id = scrapy.Field()
    rating = scrapy.Field()
    recommend_reason = scrapy.Field()
    sharing_url = scrapy.Field()
    user_uid = scrapy.Field()
    user_name = scrapy.Field()
    vote_count = scrapy.Field()

class WeiboTopicItem(scrapy.Item):
    
    type = scrapy.Field()
    weibo_movie_id = scrapy.Field()
    weibo_movie_name = scrapy.Field()
    title_sub = scrapy.Field()
    desc1 = scrapy.Field()
    desc2 = scrapy.Field()
    pic = scrapy.Field()
    item_id = scrapy.Field()
    analysis_extra = scrapy.Field()
    

class WeiboChaohuaItem(scrapy.Item):

    type            = scrapy.Field()
    chaohua_id      = scrapy.Field()
    cid             = scrapy.Field()
    nick            = scrapy.Field()
    comments_count  = scrapy.Field()
    created_at      = scrapy.Field()
    text            = scrapy.Field()
    source          = scrapy.Field()
    user_id         = scrapy.Field()
    description     = scrapy.Field()
    screen_name     = scrapy.Field()
    followers_count = scrapy.Field()
    verified_reason = scrapy.Field()


class DoubanUserFriendItem(scrapy.Item):
    
    type          = scrapy.Field()
    user_id       = scrapy.Field()
    friend_id     = scrapy.Field()
    friend_uid    = scrapy.Field()
    friend_name   = scrapy.Field()
    friend_avatar = scrapy.Field()

class DoubanUserGuangboItem(scrapy.Item):
    
    type        = scrapy.Field()
    id          = scrapy.Field()
    activity    = scrapy.Field()
    author_id   = scrapy.Field()
    author_uid  = scrapy.Field()
    create_time = scrapy.Field()
    text        = scrapy.Field()
    uri         = scrapy.Field()
    sharing_url = scrapy.Field()
    ref         = scrapy.Field()
    card        = scrapy.Field()