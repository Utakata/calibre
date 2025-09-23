#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2023, Jules'
__docformat__ = 'restructuredtext en'

from qt.core import (QDialog, QVBoxLayout, QFormLayout, QCheckBox,
                     QComboBox, QDialogButtonBox)

class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super(OptionsDialog, self).__init__(parent)
        self.setWindowTitle('Yomitoku OCR Options')

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # --- Create Widgets ---
        self.lite_model_checkbox = QCheckBox('Use lite model for faster processing', self)
        self.ignore_breaks_checkbox = QCheckBox('Join text blocks (ignore line breaks)', self)
        self.ignore_breaks_checkbox.setChecked(True) # Default to True as it's good for TTS
        self.ignore_meta_checkbox = QCheckBox('Ignore header/footer text', self)

        self.reading_order_combo = QComboBox(self)
        self.reading_order_combo.addItems(['auto', 'left2right', 'top2bottom', 'right2left'])

        # --- Add Widgets to Form ---
        self.form_layout.addRow('Model:', self.lite_model_checkbox)
        self.form_layout.addRow('Text Flow:', self.ignore_breaks_checkbox)
        self.form_layout.addRow('Content:', self.ignore_meta_checkbox)
        self.form_layout.addRow('Reading Order:', self.reading_order_combo)

        self.layout.addLayout(self.form_layout)

        # --- OK and Cancel Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

        self.options = {}

    def accept(self):
        # Store the selected options in a dictionary
        self.options = {
            'lite': self.lite_model_checkbox.isChecked(),
            'ignore_breaks': self.ignore_breaks_checkbox.isChecked(),
            'ignore_meta': self.ignore_meta_checkbox.isChecked(),
            'reading_order': self.reading_order_combo.currentText()
        }
        super(OptionsDialog, self).accept()

    # Static method to make it easy to call the dialog
    @staticmethod
    def get_options(parent=None):
        dialog = OptionsDialog(parent)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            return True, dialog.options
        return False, None
