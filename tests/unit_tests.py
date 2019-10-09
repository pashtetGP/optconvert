from unittest import TestCase
import sys
from opt_convert import Converter, Model, parse_args, command_line
from argparse import ArgumentError

Converter.setDebug(True)

class TestConverter(TestCase):

    def test__init__(self):
        Converter('instance.mps', 'mpl')
        self.assertTrue(True)

class TestModel(TestCase):

    def test__init__(self):
        Model()
        self.assertTrue(True)

class Test_command_line(TestCase):

    def test_parse_args(self):
        filename = 'instance.mps'
        fileformat = 'mpl'
        parsed = parse_args(['--file', filename, '--format', fileformat])
        self.assertEqual(parsed.file, filename)
        self.assertEqual(parsed.format, fileformat)

    def test_parse_args_no_filename(self):
        fileformat = 'mpl'
        parsed = parse_args(['--format', fileformat])
        self.assertIs(parsed.file, None)
        self.assertEqual(parsed.format, fileformat)

    def test_parse_args_no_fileformat(self):
        filename = 'instance.mps'
        parsed = parse_args(['--file', filename])
        self.assertEqual(parsed.file, filename)
        self.assertIs(parsed.format, None)

    def test_parse_args_none(self):
        parsed = parse_args([])
        self.assertIs(parsed.file, None)
        self.assertIs(parsed.format, None)

    def test_parse_args_wrong_fileformat(self):
        filename = 'instance.mps'
        fileformat = 'trk'
        with self.assertRaises(ArgumentError) as e:
            parse_args(['--file', filename, '--format', fileformat])
        self.assertEqual(str(e.exception), "argument --format: invalid choice: 'trk' (choose from None, 'mpl', 'mps')")

    def test_command_line(self):
        filename = 'instance.mps'
        fileformat = 'mpl'
        sys.argv = ['--file', filename, '--format', fileformat]
        command_line()
        self.assertTrue(True)