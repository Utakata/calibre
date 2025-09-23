#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2023, Jules'
__docformat__ = 'restructuredtext en'

from calibre.customize import EditBookToolPlugin

class YomitokuPlugin(EditBookToolPlugin):

    name = 'Yomitoku OCR'
    version = (0, 2, 0)
    author = 'Jules'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Run Yomitoku OCR on images within the Calibre Book Editor.'
    minimum_calibre_version = (5, 0, 0)

    def is_customizable(self):
        # The configuration is still needed for the yomitoku path.
        return True

    def config_widget(self):
        from calibre_plugins.yomitoku_plugin.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
