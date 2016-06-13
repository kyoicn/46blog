# -*- coding: utf-8
from ConfigParser import ConfigParser
import tweepy
import os

class TwitterBot:
    """Just tweet!
    """

    def __init__(self, config = 'config.ini'):
        # TODO: load from config
        try:
            cp = ConfigParser()
            cp.read(config)
            self._auth = tweepy.OAuthHandler(
                cp.get('General', 'twitter_consumer_key'),
                cp.get('General', 'twitter_consumer_secret'))
            self._auth.set_access_token(
                cp.get('General', 'twitter_access_token'),
                cp.get('General', 'twitter_access_secret'))
            self._api = tweepy.API(self._auth)
        except Exception as e:
            # TODO: log.aterror
            print 'An error occurred while loading config: ' + str(e)
            raise

    """Tweeeeeeeeeet
    """
    def tweet(self, entry):
        # TODO: log.atfine
        text = self._format_text(entry.get_author(),
                                 entry.get_title(),
                                 entry.get_text())
        # TODO: log.atfine
        # Cannot include more than 4 images or 1 gif
        print 'start uploading'

        # TODO: reduce
        image_ids = map(
            lambda m: m.media_id,
            map(
                self._api.media_upload,
                filter(
                    lambda i: os.stat(i).st_size <= 3000000,
                    map(
                        lambda i: i.get_local_url(),
                        filter(
                            lambda i: i.get_extension() != '.gif',
                            entry.get_images())))[:4]))
        return self._api.update_status(status = text,
                                       media_ids = image_ids)

    def _format_text(self, author = '', title = '', text = ''):
        # TODO: move 140 to config and deal with the last emis
        return unicode(
            '{0}「{1}」:{2}'.format(author, title, text)[:140],
            'utf8',
            errors = 'ignore').encode('utf8')