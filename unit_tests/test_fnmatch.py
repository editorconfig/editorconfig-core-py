import unittest

from editorconfig.fnmatch import fnmatch


class BracketTest(unittest.TestCase):

    def test_unclosed_bracket_is_literal(self):
        self.assertTrue(fnmatch('a[b', 'a[b'))
        self.assertTrue(fnmatch('[', '['))
        self.assertTrue(fnmatch('[ab', '[ab'))
        self.assertTrue(fnmatch('[!', '[!'))
        self.assertTrue(fnmatch('x[]', 'x[]'))
        self.assertFalse(fnmatch('ab', 'a[b'))

    def test_escaped_close_bracket_does_not_close(self):
        self.assertTrue(fnmatch('[a]', r'[a\]'))
        self.assertFalse(fnmatch('a', r'[a\]'))

    def test_escaped_backslash_before_close_bracket(self):
        self.assertTrue(fnmatch('\\', r'[\\]'))
        self.assertFalse(fnmatch('a', r'[\\]'))

    def test_glob_characters_inside_brackets_are_literal(self):
        self.assertTrue(fnmatch('*', '[*?]'))
        self.assertTrue(fnmatch('?', '[*?]'))
        self.assertFalse(fnmatch('a', '[*?]'))
        self.assertFalse(fnmatch('[', '[?]'))

    def test_escaped_dash_inside_brackets_is_literal(self):
        self.assertTrue(fnmatch('-', r'[a\-c]'))
        self.assertFalse(fnmatch('b', r'[a\-c]'))

    def test_slash_inside_brackets_matches_literally(self):
        self.assertTrue(fnmatch('[.+/]x', '[.+/]x'))
        self.assertFalse(fnmatch('[aa/]x', '[.+/]x'))
        self.assertTrue(fnmatch('[*/]x', '[*/]x'))
        self.assertFalse(fnmatch('[ab/]x', '[*/]x'))


if __name__ == '__main__':
    unittest.main()
