from datetime import datetime
import binascii
import calendar
import MySQLdb

class DBSaver:
    """Talks to DB"""

    def __init__(self, host, user, cred, db):
        # TODO: load from config
        self._host = host
        self._user = user
        self._cred = cred
        self._db = db
        # TODO: load necessary db data, e.g. member names

    def connect(self):
        c = MySQLdb.connect(
            use_unicode = True,
            connect_timeout = 0,
            host = self._host,
            user = self._user,
            passwd = self._cred,
            db = self._db)
        c.autocommit(True)
        return c

    def terminate(self):
        # self._conn.close();
        return

    """Save entry data to database"""
    def save(self, entry):
        # TODO: log.atfine()
        print '[{}]'.format(datetime.now()) + 'start saving to db:'
        try:
            conn = self.connect()

            sql_insert_entry = self._insert_entry_sql(entry)
            print(sql_insert_entry[:200])
            cur = conn.cursor()
            cur.execute(sql_insert_entry)
            # self._conn.commit()
            cur.close()

            sql_insert_image = self._insert_image_sql(entry)
            print(sql_insert_image[:100])
            cur = conn.cursor()
            cur.execute(sql_insert_image)
            # self._conn.commit()
            cur.close()

        except Exception as e:
            # TODO: log
            print str(e)

        finally:
            conn.close()

    def _insert_entry_sql(self, entry):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)

        # TODO: check if exist already
        
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(DBSaver._get_author_id(entry.get_author()))
        author_id = cur.fetchone()[0]
        cur.close()
        conn.close()

        sql = '''INSERT INTO entry (hashcode, publish_time, author_id,
            author_name, title, text, permalink, raw_html)
            VALUES('{}', {}, {}, '{}', '{}', '{}', '{}', '{}')'''.format(
                entry.hashcode(),
                calendar.timegm(entry.get_time().timetuple()),
                author_id,
                entry.get_author(),
                entry.get_title(),
                entry.get_text(),
                entry.get_permalink(),
                entry.get_html())

        return sql.strip()

    def _insert_image_sql(self, entry):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(DBSaver._get_entry_id(entry.hashcode()))
        entry_id = cur.fetchone()[0]
        cur.close()
        conn.close()

        values = ''
        for image in entry.get_images():
            values += "('{}', '{}', '{}', '{}', '{}', 0x{}, '{}'),".format(
                image.hashcode(),
                entry_id,
                image.get_remote_url(),
                image.get_remote_url(False),
                image.get_local_url(),
                binascii.b2a_hex(image.get_content()),
                image.get_extension())

        sql = '''INSERT INTO image (hashcode, entry_id, remote_url,
            remote_url_2, local_url, content, extension)
            VALUES {}'''.format(values[:-1])

        return sql.strip()

    @staticmethod
    def _get_entry_id(hashcode):
        sql = 'SELECT id FROM entry WHERE hashcode="{}"'.format(hashcode)
        return sql.strip()

    @staticmethod
    def _get_author_id(name):
        sql = 'SELECT id FROM member WHERE name="{}"'.format(name)
        return sql.strip()