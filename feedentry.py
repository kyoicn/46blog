from hashlib import md5
from imgfetcher import ImgFetcher
import dateutil.parser
import pytz

class FeedEntry:
    """Data structure that stores feed entry"""
    TOKYO_TZ = pytz.timezone('Asia/Tokyo')

    """Rich contents are not loaded at initialization for the sake of
    efficiency.
    """
    def __init__(self,
                 author,
                 publish_time, # ISO8601 date time format string
                 title = '',
                 text = '', # Plain text content, should be formatted
                 image_remote_urls = [],
                 image_local_urls = [],
                 permalink = '',
                 raw_html = '', # Raw HTML markup
                 raw_entry = None,
                 readonly = True
                 ):
        # Basic info in plain text
        self.info = {
            'author': author.encode('utf8'),
            'title': title.encode('utf8'),
            'publish_time': publish_time
        }
        
        # Basic contents in plain text
        self.content = {
            'text': text.encode('utf8'),
            'image_remote_urls': image_remote_urls,
            # TODO: rethink this copy of local urls
            'image_local_urls': image_local_urls
        }
        
        # Fully loaded contents richer than plain text
        self.rich_content = {
            # Datetime object
            'publish_time': dateutil.parser.parse(self.info['publish_time'])
                .astimezone(FeedEntry.TOKYO_TZ),

            # List of FeedImage
            'images': []
        }
        
        # Metadata of entry
        self._meta = {
            'permalink': permalink,
            'raw_html': raw_html.encode('utf8'),
            'raw_entry': raw_entry
        }
        
        # Config, make is static
        self._config = {
            'data_dir': 'data/',
            'readonly': readonly,
        }

        # Status
        self._images_loaded = False

    """Loads images locally or remotely"""
    # TODO: load images in parellel
    def load_images(self):
        if self._images_loaded:
            return self
        if len(self.content['image_local_urls']) > 0:
            try:
                # Build FeedImage from local files
                self.rich_content['images'] = map(lambda f: open(f, 'r'),
                    self.content['image_local_urls'])
                self._images_loaded = True
                return self
            except:
                print 'Local resource does not exist'
                pass
        self.rich_content['images'] = map(lambda f: ImgFetcher(f).fetch(),
            self.content['image_remote_urls'])
        self._images_loaded = True
        return self

    """Hashcode of an entry is based on its basic info including author, title
    and publish time. This hashcode is used as the primary key of an feed entry
    in database.
    """
    def hashcode(self):
        return md5(str(hash(frozenset(self.info.values())))).hexdigest()

    """Hashcode of entry's content which indicates the version of an entry.
    Based on raw HTML.
    """
    def content_hashcode(self):
        return md5(self._meta['raw_html']).hexdigest()

    """Helpful getters."""
    def get_author(self):
        return self.info['author']

    def get_title(self):
        return self.info['title']

    # Publish time in plain text.
    def get_time_str(self):
        return self.info['publish_time']

    # Publish time in datetime object.
    def get_time(self):
        return self.rich_content['publish_time']
        
    # Returns plain text content
    def get_text(self):
        return self.content['text']

    # Returns raw HTML markup
    def get_html(self):
        return self._meta['raw_html']

    # Returns permalink
    def get_permalink(self):
        return self._meta['permalink']
        
    # Returns full loaded FeedImage objects
    def get_images(self):
        return self.rich_content['images']

    # Returns if this instance is read-only (cannot be stored locally)
    def is_readonly(self):
        return self._config['readonly']