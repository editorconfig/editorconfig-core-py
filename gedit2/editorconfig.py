import gedit
from subprocess import Popen, PIPE, STDOUT

class EditorConfigPlugin(gedit.Plugin):
    NUMERIC_PROPERTIES = ('indent_size', 'tab_width')

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
        """Call EditorConfig core to and return properties dict for document"""

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

    def deactivate(self, window):
        handler_id = window.get_data('EditorConfigPluginHandlerId')
        window.disconnect(handler_id)
        window.set_data('EditorConfigPluginHandlerId', None)
