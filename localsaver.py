from datetime import datetime
import os

class LocalSaver:
    """Organizes local resource"""

    # File name for entry's raw content (HTML markup).
    RAW_CONTENT_FILENAME = 'raw_content.html'

    # File name for entry's plain text content.
    TEXT_CONTENT_FILENAME = 'text_content.txt'

    def __init__(self, data_dir, verbose=0):
        try:
            self._data_dir = data_dir + '/'
            self._verbose = verbose
            if self._verbose > 0:
                # TODO: log
                print('[LocalSaver] Initialized')

        except Exception as e:
            # TODO: log.aterror
            print 'An error occurred while loading config: ' + str(e)
            raise

    """Save entry data to local machine"""
    def save(self, entry):
        if entry.is_readonly():
            raise Exception(
                """
                This entry is read-only, storing operations are not allowed.
                """)
        try:
            # TODO: log.atfine()
            print '[{}]'.format(datetime.now()) + 'start saving to local:'

            time = entry.get_time()
            author = entry.get_author()
            LocalSaver._init_path(self.get_entry_path_base(time, author))
            LocalSaver._init_path(self.get_entry_path_images(time, author))

            fn = self.get_entry_filename_raw_content(time, author)
            if LocalSaver._save_file(fn, entry.get_html()):
                # TODO: log.atfine()
                print '-saved to ' + fn

            fn = self.get_entry_filename_text_content(time, author)
            if LocalSaver._save_file(fn, entry.get_text()):
                # TODO: log.atfine()
                print '-saved to ' + fn

            for index, image in enumerate(entry.get_images()):
                image_filename = (self.get_entry_path_images(time, author)
                    + image.hashcode()
                    + image.get_extension())
                if LocalSaver._save_file(image_filename, image.get_content()):
                    image.set_local_url(image_filename)
                    entry.set_image_local_url(image.get_remote_url(),
                                              image_filename)
                    # TODO: log.atfine()
                    print '-saved to ' + image_filename

            return True

        except Exception as e:
            # TODO: log
            print str(e)
            return False

    """Getter methods for local paths where the entry's data is stored."""
    # Base path.
    def get_entry_path_base(self, time, author):
        return (self._data_dir
            + time.strftime('%Y/%m/%d/')
            + author
            + time.strftime('/%H%M%S/'))

    # Images path.
    def get_entry_path_images(self, time, author):
        return self.get_entry_path_base(time, author) + 'images/'

    # Raw content (HTML source) path.
    def get_entry_filename_raw_content(self, time, author):
        return (self.get_entry_path_base(time, author)
            + LocalSaver.RAW_CONTENT_FILENAME)

    # Plain text content path.
    def get_entry_filename_text_content(self, time, author):
        return (self.get_entry_path_base(time, author)
            + LocalSaver.TEXT_CONTENT_FILENAME)

    @staticmethod
    def _init_path(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e: # Guard against race condition
                if e.errno != errno.EEXIST:
                    raise

    @staticmethod
    def _save_file(filename, file_or_content):
        try:
            try:
                file_or_content.seek(0)
                content = file_or_content.read()
            except AttributeError:
                content = file_or_content

            #LocalSaver._init_path(filename)
            with open(filename, 'w+') as f:
                f.write(content)
            return True
        except Exception as e:
            # TODO: log
            print ('An error occurred while saving to [{0}]: '.format(filename)
                + str(e))
            return False
