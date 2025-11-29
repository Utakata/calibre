
from calibre.customize import InterfaceActionBase

class NativePathPlugin(InterfaceActionBase):
    name                = 'Native Path Plugin'
    description         = 'Saves files using native characters (e.g. Japanese) instead of ASCII.'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Jules'
    version             = (1, 0, 0)
    minimum_calibre_version = (5, 0, 0)
    # The module name matches the zip filename (minus extension)
    actual_plugin       = 'calibre_plugins.NativePathPlugin.ui:NativePathAction'

    def is_customizable(self):
        return False
