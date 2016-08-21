from datetime import datetime
from sql import *
import MySQLdb

class DBSaver:
    """Talks to DB"""

    def __init__(self, host, user, cred, db):
        # TODO: load from config
        self._db = MySQLdb.connect(host = host,
                                  user = user,
                                  passwd = cred,
                                  db = db)
        self._cur = self._db.cursor()
        self._entry_table = Table('entry')
        self._member_table = Table('member')
        self._image_table = Table('image')
        # TODO: load necessary db data, e.g. member names

    """Save entry data to database"""
    def save(self, entry):
        # try:
            # TODO: log.atfine()
            print '[{}]'.format(datetime.now()) + 'start saving to db:'

            insert = self._insert_entry_sql(entry)
            #self._cur.execute(insert[0], insert[1])

            insert = self._insert_image_sql(entry)
            print insert
            self._cur.executemany(insert[0], insert[1])

            return True
        # except Exception as e:
        #     # TODO: log
        #     print str(e)
        #     return False

    def _insert_entry_sql(self, entry):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)
        # TODO: load columns from config, and use map() here
        columns = [
            self._entry_table.id,
            self._entry_table.publish_time,
            self._entry_table.author_id,
            self._entry_table.author_name,
            self._entry_table.title,
            self._entry_table.text,
            self._entry_table.permalink,
            self._entry_table.raw_html,
        ]
        values = [[
            entry.hashcode(),
            entry.get_time_str(),
            #self._name_id_map[entry.get_author()],
            1,
            entry.get_author(),
            entry.get_title(),
            entry.get_text(),
            entry.get_permalink(),
            entry.get_html()
        ]]
        return tuple(self._entry_table.insert(columns = columns,
                                              values = values))

    def _insert_image_sql(self, entry):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)
        # TODO: load columns from config, and use map() here
        columns = [
            self._image_table.id,
            self._image_table.entry_id,
            self._image_table.remote_url,
            self._image_table.remote_url_2,
            self._image_table.local_url,
            self._image_table.content,
            self._image_table.extension
        ]
        values = []
        for image in entry.get_images():
            values.append([
                image.hashcode(),
                entry.hashcode(),
                image.get_remote_url(),
                image.get_remote_url(False),
                image.get_local_url(),
                # image.get_content(),
                '',
                image.get_extension()
            ])
        return tuple(self._image_table.insert(columns = columns,
                                              values = values))