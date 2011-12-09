# EditorConfig Gedit Plugin

This is an [EditorConfig][] plugin for gedit.

## Installation

Download the [EditorConfig core][] and follow the instructions in the README
and INSTALL files to install it.

Once EditorConfig core is installed, the plugin compatible with your version of
Gedit will need to be installed.  After installing the plugin, it must be
enabled in Gedit.  To enable the plugin navigate to
*Edit* -> *Preferences* -> *Plugins* and check the EditorConfig plugin.

### Installing Plugin for Gedit 3

To install the gedit 3 plugin, copy the `editorconfig.plugin` and
`editorconfig.py` files from the `gedit3` directory to
`~/.local/share/gedit/plugins/`.


### Installing Plugin for Gedit 2

To install the gedit 2 plugin, copy the `editorconfig.gedit-plugin` and
`editorconfig.py` files from the `gedit2` directory to
`~/.gnome2/gedit/plugins/`.

## Supported properties

The EditorConfig Gedit plugin supports the following EditorConfig [properties][]:

* indent_style
* indent_size
* end_of_line
* root (only used by EditorConfig core)

With the Gedit plugin the `tab_width` property is ignored and tabs are always set to the width of `indent_size`.

[EditorConfig]: http://editorconfig.org
[EditorConfig core]: https://github.com/editorconfig/editorconfig
[properties]: http://editorconfig.org/#supported-properties
