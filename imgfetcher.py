from feedimage import FeedImage
import mimetypes
import re
import urllib2
import xml.etree.ElementTree as ET

class ImgFetcher:
    """Abstract class for fetching image from external link"""
    
    # Constant
    req_header = {
        # Chrome is the best
        'User-Agent': 'Chrome/52.0.2743.116'
    }
    # Map from image host to its specific fetching method.
    fetcher_map = {
        'default': '_fetch_default',
        'dcimg.awalker.jp': '_fetch_awalker'
    }
    
    def __init__(self, url, url_2 = '', referer=None, verbose=0):
        self._verbose = verbose
        self._url = url
        self._url_2 = url_2
        self._referer = referer

        header = ImgFetcher.req_header
        if referer:
            header['Referer'] = referer
        self._init_req = urllib2.Request(self._url,
                                         headers = header)
        self._host = str(self._init_req.get_host())
        self._idstr = 'ImgFetcher|{0}|{1}'.format(url, url_2)
        if verbose > 0:
            # TODO: log
            print('[{0}] Initialized'.format(self._idstr))

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
        
        # TODO: WORKAROUND!
        img_url_pattern = (
          r'http://dcimg\.awalker\.jp/img2\.php\?sec_key=[a-zA-Z0-9]*')
        img_url = re.search(img_url_pattern, response.read()).group(0)

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