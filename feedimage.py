from hashlib import md5

class FeedImage:
    """Data structure that stores image in feed.
    NOTE: face recognition could be a very helpful attempt to greatly enrich
    the content of this data structure, and make lots of further analysis
    possible.
    """
    
    # TODO: use image lib
    def __init__(self,
                 content, # Binary content
                 remote_url, # Primary remote url, should be immutable
                 extension = '',
                 remote_url_2 = '', # Secondary remote url, should be immutable
                 local_url = '', # Local path
                 readonly = True # Whether read-only, immutable
                 ):
        self._content = content
        self._extension = extension
        self._remote_url = remote_url
        self._remote_url_2 = remote_url_2
        self._local_url = local_url
        self._readonly = readonly

    def get_content(self):
        return self._content

    def get_extension(self):
        return self._extension

    def get_remote_url(self, primary = True):
        if primary:
            return self._remote_url
        return self._remote_url_2

    def get_local_url(self):
        return self._local_url

    def set_local_url(self, url):
        # if self._readonly:
        #     raise Exception('Read-only FeedImage')
        self._local_url = url

    def hashcode(self):
        return md5(self._remote_url).hexdigest()
