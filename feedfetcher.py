from datetime import datetime
from feedentry import FeedEntry
from localsaver import LocalSaver
from lxml import html
from tempfile import TemporaryFile
import hashlib
import re
import urllib2
import xml.etree.ElementTree as ET

class FeedFetcher:
    """Performs operations to fetch feeds.
    Store raw data to local file system.
    """

    # Constants
    req_header_with_agent = {
        # Chrome is the best
        'User-Agent': 'Chrome/52.0.2743.116'
    }

    def __init__(self,
                 feed_url,
                 data_dir,
                 cache_dir,
                 cache_feed,
                 verbose=0,
                 no_cache=False):
        self._config = {
            'feed_url': feed_url,
            'cache_dir': cache_dir + '/',
            'cache_file_name': cache_feed,
            'data_dir': data_dir + '/',
        }
        self._verbose = verbose
        self._no_cache = no_cache

        # Status
        self._status = {
            # Hashcode of last cached response
            'cache_file_hashcode':
                self._get_file_hashcode(self._config['cache_file_name']),
            # Set of hashcodes of saved entries
            'saved_entries': set()
        }

        self._feed_req = urllib2.Request(
            self._config['feed_url'],
            headers = FeedFetcher.req_header_with_agent)
        self._localsaver = LocalSaver(data_dir, verbose)

        if self._verbose > 0:
            # TODO: log
            print('[FeedFetcher:{0}] Initialized'.format(feed_url))

    """Fetches feeds and returns a list of fully loaded new FeedEntry"""
    def fetch(self,
              max_fetch = 0 # Number of entries to fetch,
                            # non-positives are ignored
              ):
        try:
            cache_tmp = TemporaryFile()
            feed_response = urllib2.urlopen(self._feed_req, timeout = 60)
            cache_tmp.write(feed_response.read())
            cache_tmp.seek(0)
        except Exception as e:
            cache_tmp.close()
            print 'While fetching response: ' + str(e)
            return

        # Compare file checksum with cached feed file, save to file if new
        # contents are available
        new_file_hashcode = self._get_file_hashcode(cache_tmp)
        if (not self._no_cache and
            new_file_hashcode == self._status['cache_file_hashcode']):
            # TODO: log.atfine()
            print (datetime.now().strftime('[%H:%M:%S]')
                + 'old version, pass')
            cache_tmp.close()
            return []

        # TODO: log.atfine
        print (datetime.now().strftime('[%H:%M:%S]')
            + 'feed has a new version: '
            + new_file_hashcode)

        # TODO: cache hashcode should be updated only after local saving is
        # successfully performed
        self._save_feed_file(cache_tmp)
        if not self._no_cache:
            self._save_cache_file(cache_tmp)
            self._status['cache_file_hashcode'] = new_file_hashcode

        # Iterate over entries and stops at last cached entry
        cache_tmp.seek(0)
        to_return = []
        added = 0
        for entry in self._parse_tree(cache_tmp):
            print 'loop'
            # check if stored
            if (not self._no_cache and
                entry.hashcode() in self._status['saved_entries']):
                # TODO: log.atfine
                print 'Cached entry'
                continue

            # TODO: log.atfine
            print 'New entry from: ' + entry.get_author()

            entry.load_images(self._verbose)

            if self._localsaver.save(entry):
                if not self._no_cache:
                    self._status['saved_entries'].add(entry.hashcode())
                to_return.append(entry)
                added += 1
                if max_fetch > 0 and added >= max_fetch:
                    break

        cache_tmp.close()
        # Should return immutable entries
        return to_return

    """Returns MD5 string of the given file object or file name"""
    def _get_file_hashcode(self, fileorname):
        try:
            try:
                fileorname.seek(0)
                return hashlib.md5(fileorname.read()).hexdigest()
            except AttributeError:
                return hashlib.md5(open(fileorname, 'rb').read()).hexdigest()
        except Exception as e:
            # TODO: log
            print ('An error occurred while hashing ['
                + (str(fileorname))
                + ']: '
                + str(e))
            return ''

    """Parses XML tree and returns a list of FeedEntry"""
    def _parse_tree(self, source):
        root = ET.parse(source).getroot()
        self._xmlns = re.search('^{.*}', root.tag).group()
        entries = []
        for child in root:
            if child.tag == self._xmlns + 'entry':
                entries.append(self._parse_entry(child, self._xmlns))
        return entries

    """Parses a single entry and returns a FeedEntry"""
    def _parse_entry(self, entry, ns):
        author = entry.find(ns + 'author').find(ns + 'name').text
        title = entry.find(ns + 'title').text
        if title == None:
          title = ''
        publish_time = entry.find(ns + 'published').text
        permalink = entry.find(ns + 'link').get('href')
        
        content = entry.find(ns + 'content')
        htmlcontent = html.fromstring(content.text)
        
        images = map(self._parse_img_urls, htmlcontent.cssselect('img'))
        
        return FeedEntry(author = author,
                         title = title,
                         publish_time = publish_time,
                         # TODO: formatted text content
                         text = htmlcontent.text_content(),
                         image_remote_urls = images,
                         permalink = permalink,
                         raw_html = content.text,
                         raw_entry = entry,
                         readonly = False)
        
    """Parses img element and returns the actual image content"""
    def _parse_img_urls(self, img):
        # If img element has an <a> parent, parse the external link
        try:
            parent = img.getparent()
        except Exception as e:
            parent = None
        if parent is not None and parent.tag == 'a':
            url = parent.get('href')
        else:
            url = img.get('src')

        return url

    def _save_cache_file(self, fileobj):
        return LocalSaver._save_file(self._config['cache_file_name'], fileobj)

    def _save_feed_file(self, fileobj):
        filename = (self._config['data_dir']
            + 'feed/feed_'
            + datetime.now().strftime('%m%d%H%M%S')
            + '.xml')
        return LocalSaver._save_file(filename, fileobj)

    def _log_start(self):
        # TODO: use logger
        print (datetime.now().strftime('%m-%d %H:%M:%S')
            + '<{0}>'.format(self.__class__.__name__))
