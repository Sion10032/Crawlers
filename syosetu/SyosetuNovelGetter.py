import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString

class SyosetuNovelGetter():
    '''Syosetu'''

    base_url = 'https://ncode.syosetu.com/'

    def __init__(self, s: requests.Session = None):
        # 使用Session来进行爬取，方便设置代理
        # Session需要设置UA
        if s == None:
            s = requests.Session()
            s.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            }
        self._session = s

    def set_session(self, s: requests.Session):
        '''
        设置session
        '''
        self._session = s

    def get_book_info(self, url):
        '''
        返回指定链接小说的信息
        包括标题、作者、简介、目录
        '''
        complete_url = url
        if not self.base_url in url:
            complete_url = self.base_url + (url if url[0] != '/' else url[1:])
        res = self._session.get(complete_url)
        dom = BeautifulSoup(res.text, 'html.parser')
        title = dom.find(class_='novel_title').get_text(strip=True)
        author = dom.find(class_='novel_writername').get_text(strip=True).split('：')[-1]
        intro = dom.find(id='novel_ex').get_text('\n', strip=True)
        catalog_dom = dom.find(class_='index_box')
        catalog = []
        title_name = ''
        for it in catalog_dom.children:
            if it == '\n':
                continue
            if it.get('class')[0] == 'chapter_title':
                if title_name != it.get_text(strip=True):
                    title_name = it.get_text(strip=True)
                    catalog.append((title_name, []))
            else:
                if catalog.__len__() == 0:
                    catalog.append((title, []))
                catalog[-1][1].append({
                    'name': it.dd.get_text(strip=True),
                    'url': it.a.get('href')
                })
        return {
            'title': title,
            'author': author,
            'intro': intro,
            'catalog': catalog
        }

    def get_chapter(self, url):
        '''
        获得指定url章节的具体内容
        '''
        complete_url = url
        if not self.base_url in url:
            complete_url = self.base_url + (url if url[0] != '/' else url[1:])
        resp = self._session.get(complete_url)
        result = { 'title': '', 'content': [] }
        dom = BeautifulSoup(resp.text, 'html.parser')
        result['title'] = dom.find(class_='novel_subtitle').get_text(strip=True)
        contents = dom.find(id='novel_honbun')
        result['content'] = [ it.get_text() for it in contents.children if it != '\n' ]
        return result
