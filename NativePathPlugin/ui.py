
from calibre.gui2.actions import InterfaceAction
from calibre.db.backend import DB
from calibre import sanitize_file_name
from calibre.constants import iswindows
from calibre.utils.localization import _
from calibre.db.constants import BOOK_ID_PATH_TEMPLATE
import os

class NativePathAction(InterfaceAction):
    name = 'Native Path Plugin'
    action_spec = ('Standardize Paths', 'folder', 'Update file paths to native characters', None)

    def genesis(self):
        # Monkey Patch DB methods
        self.original_construct_path_name = DB.construct_path_name
        self.original_construct_file_name = DB.construct_file_name

        DB.construct_path_name = self.custom_construct_path_name
        DB.construct_file_name = self.custom_construct_file_name

        # Initialize Action
        self.qaction.triggered.connect(self.update_paths)

    def custom_construct_path_name(self, db_self, book_id, title, author):
        # Logic adapted from calibre.db.backend.DB.construct_path_name
        # but using sanitize_file_name instead of ascii_filename

        book_id_str = BOOK_ID_PATH_TEMPLATE.format(book_id)
        # Use DB instance's PATH_LIMIT
        l = db_self.PATH_LIMIT - (len(book_id_str) // 2) - 2

        author = sanitize_file_name(author)[:l]
        title  = sanitize_file_name(title.lstrip())[:l].rstrip()

        if not title:
            title = 'Unknown'[:l]
        try:
            while author[-1] in (' ', '.'):
                author = author[:-1]
        except IndexError:
            author = ''
        if not author:
            author = sanitize_file_name(_('Unknown'))

        # Windows reserved names check
        WINDOWS_RESERVED_NAMES = frozenset('CON PRN AUX NUL COM1 COM2 COM3 COM4 COM5 COM6 COM7 COM8 COM9 LPT1 LPT2 LPT3 LPT4 LPT5 LPT6 LPT7 LPT8 LPT9'.split())
        if author.upper() in WINDOWS_RESERVED_NAMES:
            author += 'w'

        return f'{author}/{title}{book_id_str}'

    def custom_construct_file_name(self, db_self, book_id, title, author, extlen):
        # Logic adapted from calibre.db.backend.DB.construct_file_name

        extlen = max(extlen, 14)  # 14 accounts for ORIGINAL_EPUB
        l = (db_self.PATH_LIMIT - (extlen // 2) - 2) if iswindows else ((db_self.PATH_LIMIT - extlen - 2) // 2)
        if l < 5:
            raise ValueError(f'Extension length too long: {extlen}')

        author = sanitize_file_name(author)[:l]
        title  = sanitize_file_name(title.lstrip())[:l].rstrip()

        if not title:
            title = 'Unknown'[:l]

        name = title + ' - ' + author
        while name.endswith('.'):
            name = name[:-1]
        if not name:
            name = sanitize_file_name(_('Unknown'))
        return name

    def update_paths(self):
        # Get selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows:
            return
        ids = list(map(self.gui.library_view.model().id, rows))

        # Trigger path update
        self.gui.current_db.new_api.update_path(ids)
