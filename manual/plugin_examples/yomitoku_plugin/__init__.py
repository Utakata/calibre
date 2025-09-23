#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2023, Jules'
__docformat__ = 'restructuredtext en'

from calibre.customize import EditBookToolPlugin, InterfaceActionBase

# A single plugin package (ZIP file) can contain multiple plugin classes.
# Calibre will load each one based on its base class.

# --- Plugin for the Book Editor Toolbar ---
class YomitokuEditorTool(EditBookToolPlugin):

    name = 'Yomitoku OCR (Editor Tool)'
    version = (0, 3, 0)
    author = 'Jules'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Run Yomitoku OCR on images within the Calibre Book Editor.'
    minimum_calibre_version = (5, 0, 0)

    def is_customizable(self):
        # The configuration is shared, but we only show the button in one place
        # to avoid confusion. We'll let the InterfaceAction plugin handle it.
        return False

# --- Plugin for the Library View ---
class YomitokuLibraryAction(InterfaceActionBase):

    name                = 'Yomitoku OCR'
    description         = 'Run Yomitoku OCR on selected books or add new ones from files.'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Jules'
    version             = (0, 3, 0)
    minimum_calibre_version = (5, 0, 0)

    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    actual_plugin       = 'calibre_plugins.yomitoku_plugin.library_action:LibraryAction'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.yomitoku_plugin.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
