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

from qt.core import QAction, QMessageBox

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool

class OCRTool(Tool):

    name = 'yomitoku-ocr-tool'
    allowed_in_toolbar = True
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        ac = QAction('Run Yomitoku OCR', self.gui)
        ac.triggered.connect(self.run_ocr)
        return ac

    def run_ocr(self):
        # Move imports inside the method to prevent issues with plugin loading
        from calibre_plugins.yomitoku_plugin.config import prefs
        from calibre_plugins.yomitoku_plugin.options_dialog import OptionsDialog

        # Show the options dialog first
        ok, options = OptionsDialog.get_options(self.gui)
        if not ok:
            return  # User cancelled

        boss = self.boss
        current_file_name = boss.exploder_view.current_file

        if not current_file_name:
            return self.gui.status_bar.showMessage('No file selected.')

        container = boss.current_container
        mime_type = container.mime_map.get(current_file_name)
        if not mime_type or not mime_type.startswith('image/'):
            return QMessageBox.warning(self.gui, 'Not an Image', 'Please select an image file to run OCR.')

        image_data = container.raw_data_for(current_file_name)

        temp_image_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=os.path.splitext(current_file_name)[1]) as temp_image_file:
                temp_image_file.write(image_data)
                temp_image_path = temp_image_file.name

            yomitoku_path = prefs['yomitoku_path']
            if not yomitoku_path or not os.path.exists(yomitoku_path):
                return QMessageBox.critical(self.gui, 'Yomitoku Not Found', 'Please configure the path to the yomitoku executable.')

            html_to_modify = self.find_html_container_for_image(container, current_file_name)
            if not html_to_modify:
                return QMessageBox.warning(self.gui, 'Error', 'Could not find the HTML file containing the selected image.')

            with tempfile.TemporaryDirectory() as temp_dir:
                # Dynamically build the command based on user options
                command = [yomitoku_path, temp_image_path, '-f', 'json', '-o', temp_dir]
                if options['lite']:
                    command.append('-l')
                if options['ignore_breaks']:
                    command.append('--ignore_line_break')
                if options['ignore_meta']:
                    command.append('--ignore_meta')
                if options['reading_order'] != 'auto':
                    command.append('--reading_order')
                    command.append(options['reading_order'])

                subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')

                json_file_name = os.path.splitext(os.path.basename(temp_image_path))[0] + '.json'
                json_file_path = os.path.join(temp_dir, json_file_name)

                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                all_text = self.extract_text_from_json(data)

                root = container.parsed(html_to_modify)

                target_img_tag = self.find_image_tag_in_html(container, root, current_file_name, html_to_modify)
                if target_img_tag is None:
                    raise Exception("Could not find the <img> tag in the HTML file.")

                text_block_html = "".join(f"<p>{line.strip()}</p>" for line in all_text if line.strip())
                new_div = etree.fromstring(f'<div class="yomitoku_ocr_text" style="font-size: 1.2em; line-height: 1.6;">{text_block_html}</div>')

                parent = target_img_tag.getparent()
                parent.addnext(new_div)

                container.dirty(html_to_modify)

                boss.add_savepoint('Before: Yomitoku OCR')
                boss.commit_all_editors_to_container()
                boss.apply_container_update_to_gui()

                QMessageBox.information(self.gui, 'OCR Complete', 'Successfully added OCR text to the book.')

        except Exception as e:
            QMessageBox.critical(self.gui, 'Error', f"An error occurred during OCR processing: {e}")
        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    def find_html_container_for_image(self, container, image_name):
        for html_name in container.html_file_names:
            if image_name in container.references_for(html_name):
                return html_name
        return None

    def find_image_tag_in_html(self, container, root, image_name, base_html):
        for img_tag in root.xpath('//*[local-name()="img"]'):
            src = img_tag.get('src')
            if src:
                referenced_name = container.href_to_name(src, base=base_html)
                if referenced_name == image_name:
                    return img_tag
        return None

    def extract_text_from_json(self, data):
        all_text = []
        def find_text_recursively(d):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k == 'text':
                        all_text.append(v)
                    else:
                        find_text_recursively(v)
            elif isinstance(d, list):
                for item in d:
                    find_text_recursively(item)
        find_text_recursively(data)
        return all_text
