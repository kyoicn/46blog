from datetime import datetime
import binascii
import calendar
import MySQLdb

class DBSaver:
    """Talks to DB"""

    def __init__(self, host, user, cred, db):
        # TODO: load from config
        self._conn = MySQLdb.connect(
            use_unicode = True,
            host = host,
            user = user,
            passwd = cred,
            db = db)
        # TODO: load necessary db data, e.g. member names

    def terminate(self):
        self._conn.close();

    """Save entry data to database"""
    def save(self, entry):
        # try:
            # TODO: log.atfine()
            print '[{}]'.format(datetime.now()) + 'start saving to db:'

            sql_insert_entry = self._insert_entry_sql(entry)
            print(sql_insert_entry[:100])
            sql_insert_image = self._insert_image_sql(entry)
            print(sql_insert_image[:100])

            cur = self._conn.cursor()
            cur.execute(sql_insert_image)
            cur.execute(sql_insert_entry)
            
            self._conn.commit()

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

        # TODO: check if exist already
        # TODO: query author id
        author_id = 1
        sql = '''
            INSERT INTO entry (id, publish_time, author_id, author_name,
            title, text, permalink, raw_html)
            VALUES('{}', {}, {}, '{}', '{}', '{}', '{}', '{}')'''.format(
                entry.hashcode(),
                calendar.timegm(entry.get_time().timetuple()),
                author_id,
                entry.get_author(),
                entry.get_title(),
                entry.get_text(),
                entry.get_permalink(),
                entry.get_html())

        return sql

    def _insert_image_sql(self, entry):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)

        values = ''
        for image in entry.get_images():
            values += "('{}', '{}', '{}', '{}', '{}', 0x{}, '{}'),".format(
                image.hashcode(),
                entry.hashcode(),
                image.get_remote_url(),
                image.get_remote_url(False),
                image.get_local_url(),
                binascii.b2a_hex(image.get_content()),
                # image.get_content(),
                image.get_extension())

        sql = '''
            INSERT INTO image (id, entry_id, remote_url, remote_url_2,
            local_url, content, extension)
            VALUES {}'''.format(values[:-1])

        return sql