# Copyright (c) 2011-2012 EditorConfig Team
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from subprocess import Popen, PIPE, STDOUT
from gi.repository import GObject, Gedit

class EditorConfigPlugin(GObject.Object, Gedit.WindowActivatable):
    NUMERIC_PROPERTIES = ('indent_size', 'tab_width')
    __gtype_name__ = "EditorConfig"
    window = GObject.property(type=Gedit.Window)

    def do_activate(self):
        handler_id = self.window.connect('active_tab_state_changed',
                self.set_config)
        self.window.set_data('EditorConfigPluginHandlerId', handler_id)

    def set_config(self, window):
        """Get EditorConfig properties for file and change settings"""

        tab = window.get_active_tab()
        document = tab.get_document()
        view = tab.get_view()

        props = self.get_properties(document)
        self.process_properties(props)
        self.set_indentation(view,
                             props.get('indent_style'),
                             props.get('indent_size'),
                             props.get('tab_width'))
        self.set_end_of_line(document, props.get('end_of_line'))

    def get_properties(self, document):
        """Call EditorConfig core to and return properties dict for document"""

        if document:
            file_uri = document.get_uri_for_display()
            if file_uri:
                args = ['editorconfig', file_uri]
                proc = Popen(args, stdout=PIPE, stderr=STDOUT)
                lines = proc.communicate()[0].split('\n')
                return dict([p.split('=', 1) for p in lines if p.count('=')])
        return {}

    def process_properties(self, properties):
        """Process property values and remove invalid properties"""

        # Convert any numeric properties to numbers and remove invalid values
        for prop in self.NUMERIC_PROPERTIES:
            if prop in properties:
                try:
                    properties[prop] = int(properties[prop])
                except ValueError:
                    del properties[prop]

    def set_end_of_line(self, document, end_of_line):
        """Set line ending style based on given end_of_line property"""
        if end_of_line == "lf":
            document.set_property('newline-type', 0)
        elif end_of_line == "cr":
            document.set_property('newline-type', 1)
        elif end_of_line == "crlf":
            document.set_property('newline-type', 2)

    def set_indentation(self, view, indent_style, indent_size, tab_width):
        """Set indentation style for given view based on given properties"""

        if indent_style == 'space':
            view.set_insert_spaces_instead_of_tabs(True)
            if indent_size:
                view.set_tab_width(indent_size)
        elif indent_style == 'tab':
            view.set_insert_spaces_instead_of_tabs(False)
            if tab_width:
                view.set_tab_width(tab_width)

    def do_deactivate(self):
        handler_id = self.window.get_data('EditorConfigPluginHandlerId')
        self.window.disconnect(handler_id)
        self.window.set_data('EditorConfigPluginHandlerId', None)
