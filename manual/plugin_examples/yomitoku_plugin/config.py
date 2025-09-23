#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2023, Jules'
__docformat__ = 'restructuredtext en'

from qt.core import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                     QPushButton, QFileDialog)

from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/yomitoku_plugin')
prefs.defaults['yomitoku_path'] = ''

class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        info_label = QLabel(
            'This plugin requires the yomitoku command-line tool. '
            'For installation instructions, please visit the project page: '
            '<a href="https://github.com/kotaro-kinoshita/yomitoku">yomitoku on GitHub</a>'
        )
        info_label.setOpenExternalLinks(True)
        self.l.addWidget(info_label)

        path_layout = QHBoxLayout()

        path_label = QLabel('Yomitoku executable path:')
        path_layout.addWidget(path_label)

        self.path_edit = QLineEdit(self)
        self.path_edit.setText(prefs['yomitoku_path'])
        path_layout.addWidget(self.path_edit)
        path_label.setBuddy(self.path_edit)

        browse_button = QPushButton('Browse', self)
        browse_button.clicked.connect(self.select_yomitoku_path)
        path_layout.addWidget(browse_button)

        self.l.addLayout(path_layout)
        self.l.addStretch()

    def select_yomitoku_path(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            'Select yomitoku executable',
            '' # starting directory
        )
        if file:
            self.path_edit.setText(file)

    def save_settings(self):
        prefs['yomitoku_path'] = self.path_edit.text()
