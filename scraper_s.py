import re
import scrapy
import logging

COMPONENTS = {'images': "image", 'video': "video", 'likes': "like", 
              'followers': "follow"}
ONLYFANS_COUNTRY = '//*[contains(@href, "icon-location")]/../following-sibling::span/p/text()'
ONLYFANS_COUNTRY = '//*[contains(@href, "icon-location")]/../following-sibling::span/p'
WARNING = re.compile(r'warning\W*$', re.I)
SENTENCE = re.compile(r'(?!\S)\.\s+')
DISCLAIMER = re.compile(r'(legal (action|note)|creative work|disclaimer|you do not have|rights .*(belong|owned)|rights reserved|by law| permi|forbidden|protected|copyright|lawful|property|DCMA|DMCA|lawsuit|prosecute|legal|jurisdiction|distribut|enforcement|screenshot|acknowledge and agree|proprietary|prohibit|trademark| own .*content|content .+ own|any material|purchased through|unauth|reproduc|copy|terms and conditions)', re.I)
TAG = re.compile(r'(.+) (\d+)\s*$')
ONLYFANS_URL = re.compile(r'onlyfans.com\/([a-zA-Z0-9\.\-_]+)')

def strip_disclaimer(text):
    """
    Remove disclaimer text
    """
    logging.info(text)
    out = []
    for paragraph in re.split('\n', text):
        logging.info(f'<p>: [{paragraph}]')
        sentences = SENTENCE.split(paragraph)
        logging.info(f'<s>: {sentences}')
        good = '. '.join([WARNING.sub('', _s)
                          for _s in sentences if not DISCLAIMER.search(_s)])
        out.append(good)
    return '\n'.join(out)


def intify(stringval: str):
    last_char = stringval[-1]
    if re.match('\d', last_char):
        factor = 1
    else:
        stringval = stringval[:-1]
        if last_char in ('K', 'k'):
            factor = 1e3
        elif last_char in ('M', 'm'):
            factor = 1e6
    return int(float(stringval) * factor)

class OnlyfansSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://onlyfans.com/mikachu22']
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
    }
    def parse(self, response):
        yield self.info(response)
    
    def __header_info(self, response, component: str) -> str:
        _e = response.selector.xpath(f'//*[contains(@href,"icon-{component}")]/../following-sibling::span/text()')
        return intify(_e.get())


    def __pic_count(self) -> int:
        return self.__header_info(COMPONENTS['images'])
    
    
    def __video_count(self) -> int:
        return self.__header_info(COMPONENTS['video'])
    
    def __like_count(self) -> int:
        return self.__header_info(COMPONENTS['likes'])
    
    def __followers_count(self) -> int:
        return self.__header_info(COMPONENTS['followers'])
    
    def __country(self, response) -> str:
        _e = response.selector.xpath(ONLYFANS_COUNTRY)
        return _e.get()

    
    def __description(self, response) -> str:
        # _img = response.css(".b-user-info__text::text")
        # return strip_disclaimer(_img.get())
        return response.css("div.b-user-info__text > p")#.extract()

    
    def __user_name(self, response) -> str:
        _img = response.css("div.g-user-name::text")
        return _img.get()

    def __main_image(self, response) -> str:
        _img = response.css("img.b-profile__header__cover-img::attr(src)")
        return _img.extract()
    
    def __avatar_image(self, response) -> str:
        _img = response.css("div.b-profile__user > a.g-avatar > img::attr(src)")
        return _img.extract()
    
    def __subscription_text(self, response) -> str:
        _s = response.css('div.b-offer-join::text')
        return _s.get().replace('SUBSCRIBE\n', '')
   
    def __offers_text(self, response) -> list:
        offers = response.css('div.m-promotion > div.g-btn::text')
        return [_o.get().replace('\n', ' ') for _o in offers]
    
    def __tags(self, response) -> dict:
        tags = {}
        for _e in response.css('span.b-tabs__nav__text::text'):
            _m = TAG.match(_e.get())
            if _m and _m.group(1) != 'All':
                tags[_m.group(1).lower()] = int(_m.group(2))
        return tags
        
    def get_media_summary(self, response):
        pics = self.__pic_count(response)
        videos = self.__video_count(response)
        if pics or videos:
            return {'photo': pics, 'video': videos}
        return {}

    def info(self, response):
        account = ONLYFANS_URL.search(response.url).group(1)
        out = {
            'account': account,
            'description': self.__description(response),
            # 'user_name': self.__user_name(response),
            # 'country': self.__country(response),
            # 'photo': self.__main_image(response),
            # 'avatar': self.__avatar_image(response),
            # 'cost': self.__subscription_text(response),
            # 'offers': self.__offers_text(response),
            # 'followers': self.__followers_count(response),
            # 'likes': self.__like_count(response),
            # 'tags': self.__tags(response),
            # 'media': self.get_media_summary(response),
        }
        return out
