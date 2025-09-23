#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2023, Jules'
__docformat__ = 'restructuredtext en'

import os
import tempfile
import subprocess
import json
from lxml import etree

from qt.core import QMessageBox, QProgressDialog
from calibre.gui2.actions import InterfaceAction
from calibre.ebooks.oeb.polish.container import get_container

# To reuse logic and dialogs
from calibre_plugins.yomitoku_plugin.config import prefs
from calibre_plugins.yomitoku_plugin.options_dialog import OptionsDialog
from calibre_plugins.yomitoku_plugin.utils import extract_text_from_json

class LibraryAction(InterfaceAction):

    name = 'Yomitoku Library Action'
    action_spec = ('OCR Whole Book', None, 'Run Yomitoku OCR on the selected book(s)', None)

    def genesis(self):
        self.qaction.triggered.connect(self.run_whole_book_ocr)

    def run_whole_book_ocr(self):
        book_ids = self.gui.library_view.get_selected_ids()
        if not book_ids:
            return QMessageBox.warning(self.gui, 'No Books Selected', 'Please select at least one book.')
        if len(book_ids) > 1:
            return QMessageBox.warning(self.gui, 'Multiple Books', 'Please select only one book.')

        book_id = book_ids[0]
        db = self.gui.current_db.new_api

        fmt = self.get_supported_format(db, book_id)
        if not fmt:
            return QMessageBox.warning(self.gui, 'No Supported Format', 'The book is not in a supported format (EPUB, AZW3, ZIP, CBZ).')

        container = get_container(db.format(book_id, fmt, as_file=True), fmt)
        image_names = [name for name, mime in container.mime_map.items() if mime.startswith('image/')]
        if not image_names:
            return QMessageBox.information(self.gui, 'No Images', 'No images were found in the selected book.')

        ok, options = OptionsDialog.get_options(self.gui)
        if not ok: return

        yomitoku_path = prefs['yomitoku_path']
        if not yomitoku_path or not os.path.exists(yomitoku_path):
            return QMessageBox.critical(self.gui, 'Yomitoku Not Found', 'Please configure the path to the yomitoku executable.')

        ocr_results = self.perform_batch_ocr(image_names, container, yomitoku_path, options)

        if ocr_results:
            if self.inject_text_into_book(container, ocr_results):
                self.save_book(db, book_id, fmt, container)
            else:
                QMessageBox.information(self.gui, 'No Changes', 'OCR was run, but no text was inserted into the book.')
        else:
            QMessageBox.warning(self.gui, 'OCR Failed', 'Could not process any images in the book.')

    def get_supported_format(self, db, book_id):
        for f in ['epub', 'azw3']: # Only formats that can be modified
            if db.has_format(book_id, f):
                return f
        return None

    def perform_batch_ocr(self, image_names, container, yomitoku_path, options):
        ocr_results = {}
        with tempfile.TemporaryDirectory() as temp_dir:
            progress = QProgressDialog('Running OCR on book...', 'Cancel', 0, len(image_names), self.gui)
            progress.setModal(True)
            progress.setValue(0)

            for i, image_name in enumerate(image_names):
                progress.setValue(i)
                if progress.wasCanceled():
                    break

                image_data = container.raw_data_for(image_name)
                safe_filename = image_name.replace('/', '_')
                temp_image_path = os.path.join(temp_dir, safe_filename)
                with open(temp_image_path, 'wb') as f:
                    f.write(image_data)

                try:
                    with tempfile.TemporaryDirectory() as ocr_output_dir:
                        command = [yomitoku_path, temp_image_path, '-f', 'json', '-o', ocr_output_dir]
                        if options['lite']: command.append('-l')
                        if options['ignore_breaks']: command.append('--ignore_line_break')
                        if options['ignore_meta']: command.append('--ignore_meta')
                        if options['reading_order'] != 'auto':
                            command.extend(['--reading_order', options['reading_order']])

                        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')

                        json_file_name = os.path.splitext(os.path.basename(temp_image_path))[0] + '.json'
                        json_file_path = os.path.join(ocr_output_dir, json_file_name)

                        with open(json_file_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)

                        ocr_results[image_name] = extract_text_from_json(json_data)
                except Exception as e:
                    print(f"Failed to OCR {image_name}: {e}")
                    continue

            progress.setValue(len(image_names))
        return ocr_results

    def inject_text_into_book(self, container, ocr_results):
        modified_html_files = set()
        for html_name in container.html_file_names:
            root = container.parsed(html_name)
            for img_tag in root.xpath('//*[local-name()="img"]'):
                src = img_tag.get('src')
                if not src: continue

                image_name = container.href_to_name(src, base=html_name)

                if image_name in ocr_results:
                    ocr_text = ocr_results[image_name]
                    if not ocr_text: continue

                    text_block_html = "".join(f"<p>{line.strip()}</p>" for line in ocr_text if line.strip())
                    new_div = etree.fromstring(f'<div class="yomitoku_ocr_text">{text_block_html}</div>')

                    parent = img_tag.getparent()
                    parent.addnext(new_div)
                    modified_html_files.add(html_name)

        for html_name in modified_html_files:
            container.dirty(html_name)

        return len(modified_html_files) > 0

    def save_book(self, db, book_id, fmt, container):
        from calibre.ebooks.oeb.polish.main import polish_epub
        from io import BytesIO

        # Polish the book to save the changes
        opts = db.prefs
        stream = BytesIO()
        polish_epub(container, stream, opts)
        stream.seek(0)

        # Add the modified file back to the database
        db.add_format(book_id, fmt, stream, run_hooks=False)
        QMessageBox.information(self.gui, 'Success', 'Successfully added OCR text to the book.')
