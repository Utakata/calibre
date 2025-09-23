#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2023, Jules'
__docformat__ = 'restructuredtext en'

def extract_text_from_json(data):
    """
    Recursively finds all values associated with the key 'text'
    in a nested dictionary or list.
    """
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
