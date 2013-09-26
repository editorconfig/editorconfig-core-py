from os.path import abspath
import sys
import logging

editorconfig_path = abspath('../editorconfig-core-py/')
if editorconfig_path not in sys.path:
    sys.path.append(editorconfig_path)

from editorconfig import get_properties, EditorConfigError


class EditorConfigPluginMixin(object):

    def activate_plugin(self, window):
        handler_id = window.connect('active_tab_state_changed',
                self.set_config)
        window.editorconfig_handler = handler_id

    def deactivate_plugin(self, window):
        window.disconnect(window.editorconfig_handler)
        window.editorconfig_handler = None
        for document in window.get_documents():
            if getattr(document, 'editorconfig_whitespace_handler', None):
                document.disconnect(document.editorconfig_whitespace_handler)
                document.editorconfig_whitespace_handler = None

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
        self.set_trim_trailing_whitespace(document,
                props.get('trim_trailing_whitespace'))

    def get_properties_from_filename(self, filename):
        """Retrieve dict of EditorConfig properties for the given filename"""
        try:
            return get_properties(filename)
        except EditorConfigError:
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
            if (properties['indent_size'] == "tab" and
                'tab_width' in properties):
                properties['indent_size'] = properties['tab_width']
            else:
                try:
                    properties['indent_size'] = int(properties['indent_size'])
                except ValueError:
                    del properties['indent_size']

        if properties.get('trim_trailing_whitespace') == 'true':
            properties['trim_trailing_whitespace'] = True
        else:
            properties['trim_trailing_whitespace'] = False

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

    def set_trim_trailing_whitespace(self, document, trim_trailing_whitespace):
        """Create/delete file save handler for trimming trailing whitespace"""
        def trim_whitespace_on_save(document, *args):
            document.begin_user_action()
            self.trim_trailing_whitespace(document)
            document.end_user_action()
        handler_id = getattr(document, 'editorconfig_whitespace_handler', None)
        if trim_trailing_whitespace and not handler_id:
            # The trimmer does not exist, so install it:
            handler_id = document.connect('save', trim_whitespace_on_save)
            document.editorconfig_whitespace_handler = handler_id
        elif not trim_trailing_whitespace and handler_id:
            # The trimmer exists, so remove it:
            document.disconnect(document.editorconfig_whitespace_handler)
            document.editorconfig_whitespace_handler = None

    def trim_trailing_whitespace(self, document):
        """Trim trailing whitespace from each line of document"""
        for line in range(document.get_end_iter().get_line() + 1):
            end_of_line = document.get_iter_at_line(line)
            end_of_line.forward_to_line_end()
            whitespace_start = end_of_line.copy()
            while whitespace_start.backward_char():
                if not whitespace_start.get_char() in ' \t':
                    whitespace_start.forward_char()
                    break
            if not whitespace_start.equal(end_of_line):
                document.delete(whitespace_start, end_of_line)
