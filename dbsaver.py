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
        try:
            # TODO: log.atfine()
            print '[{}]'.format(datetime.now()) + 'start saving to db:'

            sql_insert_entry = self._insert_entry_sql(entry)
            print(sql_insert_entry[:200])
            cur = self._conn.cursor()
            cur.execute(sql_insert_entry)
            self._conn.commit()
            cur.close()

            cur = self._conn.cursor()
            cur.execute(DBSaver._get_entry_id(entry.hashcode()))
            entry_id = cur.fetchone()[0]
            cur.close()

            sql_insert_image = self._insert_image_sql(entry, entry_id)
            print(sql_insert_image[:100])
            cur = self._conn.cursor()
            cur.execute(sql_insert_image)
            self._conn.commit()
            cur.close()

        except Exception as e:
            # TODO: log
            print str(e)

    def _insert_entry_sql(self, entry):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)

        # TODO: check if exist already
        
        cur = self._conn.cursor()
        cur.execute(DBSaver._get_author_id(entry.get_author()))
        author_id = cur.fetchone()[0]
        cur.close()

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

        print(entry.hashcode())
        return sql.strip()

    def _insert_image_sql(self, entry, entry_id):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)

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
            print(image.hashcode())

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