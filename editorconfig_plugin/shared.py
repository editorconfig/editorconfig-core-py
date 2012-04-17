import logging
from editorconfig import get_properties, EditorConfigError


class EditorConfigPluginMixin(object):
    def set_config(self, window):
        """Get EditorConfig properties for file and change settings"""

        tab = window.get_active_tab()
        document = tab.get_document()
        view = tab.get_view()

        props = self.get_document_properties(document)
        self.process_properties(props)
        self.set_indentation(view,
                             props.get('indent_style'),
                             props.get('indent_size'),
                             props.get('tab_width'))
        self.set_end_of_line(document, props.get('end_of_line'))

    def get_properties_from_filename(self, filename):
        """Retrieve dict of EditorConfig properties for the given filename"""
        try:
            return get_properties(filename)
        except EditorConfigError as e:
            logging.error("Error reading EditorConfig file", exc_info=True)
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
