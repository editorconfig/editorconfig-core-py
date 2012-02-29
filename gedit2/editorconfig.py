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

import gedit
from subprocess import Popen, PIPE, STDOUT

class EditorConfigPlugin(gedit.Plugin):
    def activate(self, window):
        handler_id = window.connect('active_tab_state_changed', self.set_config)
        window.set_data('EditorConfigPluginHandlerId', handler_id)

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
        """Call EditorConfig core and return properties dict for document"""

        if document:
            file_uri = document.get_uri()
            if file_uri and file_uri.startswith("file:///"):
                args = ['editorconfig', file_uri[7:]]
                proc = Popen(args, stdout=PIPE, stderr=STDOUT)
                lines = proc.communicate()[0].split('\n')
                return dict([p.split('=', 1) for p in lines if p.count('=')])
        return {}

    def process_properties(self, properties):
        """Process property values and remove invalid properties"""

        # Convert tab_width to a number
        if 'tab_width' in properties:
            try:
                properties['tab_width'] = int(properties['tab_width'])
            except ValueError:
                del properties['tab_width']

        # Convert indent_size to a number or set equal to tab_width
        if 'indent_size' in properties:
            if properties['indent_size'] == "tab" and 'tab_width' in properties:
                properties['indent_size'] = properties['tab_width']
            else:
                try:
                    properties['indent_size'] = int(properties['indent_size'])
                except ValueError:
                    del properties['indent_size']

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

    def deactivate(self, window):
        handler_id = window.get_data('EditorConfigPluginHandlerId')
        window.disconnect(handler_id)
        window.set_data('EditorConfigPluginHandlerId', None)
