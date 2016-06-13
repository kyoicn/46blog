from feedimage import FeedImage
import mimetypes
import urllib2
import xml.etree.ElementTree as ET

class ImgFetcher:
    """Abstract class for fetching image from external link"""
    
    # Constant
    req_header = {
        'User-Agent': 'Magic browser'
    }
    # Map from image host to its specific fetching method.
    fetcher_map = {
        'default': '_fetch_default',
        'dcimg.awalker.jp': '_fetch_awalker'
    }
    
    def __init__(self, url, url_2 = ''):
        self._url = url
        self._url_2 = url_2
        self._init_req = urllib2.Request(self._url,
                                         headers = ImgFetcher.req_header)
        self._host = str(self._init_req.get_host())

    def fetch(self):
        try:
            fetcher = getattr(self, ImgFetcher.fetcher_map[self._host])
        except:
            fetcher = getattr(self, ImgFetcher.fetcher_map['default'])
        # TOOD: log
        print 'Start fetching image from [' + self._host + ']'
        # TODO: reconsider this part
        try:
            return fetcher()
        except Exception as e:
            # TODO: at error
            print 'Error loading remote resource:' + str(e)
        
    def _fetch_default(self):
        response = urllib2.urlopen(self._init_req, timeout = 60)
        extension = mimetypes.guess_extension(response.info().getheader(
            'Content-Type'))
        return self._new_feed_image(response.read(), extension)
        
    def _fetch_awalker(self):
        response = urllib2.urlopen(self._init_req, timeout = 60)
        cookie = response.info().getheader('Set-Cookie')
        
        # TODO: update this
        dom = ET.parse(response).getroot()
        img_url = dom.iter('img').next().get('src')

        req = urllib2.Request(img_url, headers = ImgFetcher.req_header)
        req.add_header('Referer', self._url)
        req.add_header('Cookie', cookie)
        
        res = urllib2.urlopen(req)
        return self._new_feed_image(res.read())

    def _new_feed_image(self, content, extension = '.jpg'):
        return FeedImage(content = content,
                         remote_url = self._url,
                         remote_url_2 = self._url_2,
                         extension = extension,
                         readonly = False)