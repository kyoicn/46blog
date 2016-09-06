# -*- coding: utf-8
from ConfigParser import ConfigParser
import math
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
        tweets = self.prepare(entry)
        # TODO: log.atfine
        print 'Start tweeting ' + str(len(tweets)) + ' tweets:'
        for tweet in tweets:
            print(tweet)
            self._api.update_status(
                status = tweet["text"],
                media_ids = tweet["image_ids"])

    def prepare(self, entry):
        # Cannot include more than 4 images or 1 gif
        # return a list of prepared tweets, including text and pics
        images_to_upload = filter(
            # TODO: handle oversize images
            lambda i: os.stat(i).st_size <= 3000000,
            map(
                lambda i: i.get_local_url(),
                filter(
                    lambda i: i.get_extension() != '.gif',
                    entry.get_images())))
        print 'Uploading ' + str(len(images_to_upload)) + ' images'
        image_ids = map(
            lambda m: m.media_id,
            map(self._api.media_upload, images_to_upload))

        tweets = []
        n = len(image_ids)
        count = int(math.ceil(1.0 * n / 4))
        idx = 1
        while n > 0:
            print count
            print idx
            tweet = {
                "text": TwitterBot._format_text(entry, count, idx),
                "image_ids": image_ids[(idx - 1) * 4:idx * 4]
            }
            tweets.append(tweet)
            n -= 4
            idx += 1

        return tweets

    @staticmethod
    def _format_text(entry=None, count=1, idx=1):
        # PATTERN: #乃木坂46 #$AUTHOR「$TITLE」：$CONTENT… $LINK[ $IDX/$COUNT]
        author = entry.get_author()
        title = entry.get_title()
        link = entry.get_permalink()
        content = entry.get_text()

        author_length = len(author)
        title_length = len(title)
        content_length = len(content)

        pattern = '#乃木坂46 #{0}「{1}」：{2} {3}'.format
        counter_pattern = ''.format
        reserved_length = 35
        if count > 1:
            counter_pattern = ' {0}/{1}'.format
            reserved_length = 41

        space_for_title = 140 - reserved_length - author_length
        print reserved_length
        print space_for_title
        print title_length
        if title_length > space_for_title:
            title = title[0:space_for_title] + '…'
            title_length = len(title)
        space_for_content = 140 - reserved_length - author_length - title_length
        print space_for_content
        print content_length
        if content_length > space_for_content:
            content = content[0:space_for_content] + '…'
        print content
        text = (pattern(author, title, content, link)
            + counter_pattern(idx, count))
        print text
        return unicode(
            text,
            'utf8',
            errors = 'ignore').encode('utf8')