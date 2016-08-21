#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import print_function
from ConfigParser import ConfigParser
from dbsaver import DBSaver
from feedfetcher import FeedFetcher
from twitterbot import TwitterBot
import argparse
import sys
import time

argparser = argparse.ArgumentParser(
    prog = '46blog bot',
    description = 'Options for fetching, parsing, saving and tweeting data.',
    epilog = 'うちらは乃木坂登り坂！')
argparser.add_argument(
    '-v', '--verbose',
    action = 'count',
    default = 0,
    help = 'verbose output, use multiple times to indicate verbosity level')
argparser.add_argument(
    '-f', '--no_cache',
    action = 'store_true',
    help = '''disable comparing with cached feed,
              all fetches are considered as new''')
argparser.add_argument(
    '-t', '--twitter',
    action = 'store_true',
    help = 'enable to tweet new posts')
argparser.add_argument(
    '-d', '--database',
    action = 'store_true',
    help = 'enable to store in database')
argparser.add_argument(
    '-b', '--interval',
    action = 'store',
    type = int,
    default = 60,
    help = 'interval in seconds between two rounds of fetches, default 60s')
argparser.add_argument(
    '-m', '--max_fetch',
    action = 'store',
    type = int,
    default = 0,
    help = '''max number of blog posts to fetch in each round,
              if set to non-positive then unlimited''')
argparser.add_argument(
    '-c', '--config_file',
    action = 'store',
    type = str,
    default = 'config.ini',
    help = 'specify config file, default is config.ini')

args = argparser.parse_args()
if args.verbose > 0:
    print(vars(args))

cp = ConfigParser()
cp.read(args.config_file)

fetcher = FeedFetcher(args.config_file, args)

if args.twitter:
    twitter_bot = TwitterBot(args.config_file)
    tweeted_file = open(cp.get('General', 'tweeted'), 'r+')
    tweeted = set(tweeted_file.read().split('\n'))

if args.database:
    db_saver = DBSaver()

while True:
    try:
        for entry in reversed(fetcher.fetch(max_fetch = args.max_fetch)):
            # Main loop

            # DB saver
            # TODO: async
            if args.database:
                if args.verbose > 0:
                    print('save to db')

            # Twitter bot
            # TODO: async
            if args.twitter:
                if entry.hashcode() not in tweeted:
                    twitter_bot.tweet(entry)
                    tweeted.add(entry.hashcode())
                    tweeted_file.write('{}\n'.format(entry.hashcode()))
                    print('tweeted: {0}/{1}'.format(
                        entry.get_author(),
                        entry.get_title()))

        time.sleep(args.interval)

    except KeyboardInterrupt:
        if args.verbose > 0:
            print('Keyboard Interrupt: clean up')
        if args.twitter:
            if args.verbose > 0:
                print('...closing tweeted_file', end = '')
            tweeted_file.close()
            if args.verbose > 0:
                print('[OK]')
        if args.database:
            if args.verbose > 0:
                print('...closing db connection', end='')
            # close connection
            if args.verbose > 0:
                print('[OK]')

        sys.exit('The bot is terminated by you.')

    except Exception as e:
        print(str(e))