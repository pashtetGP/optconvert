from unittest import TestCase
from unittest.mock import patch
import sys
from opt_convert import Converter, Model, parse_args, command_line
from argparse import ArgumentError
from pathlib import Path

Converter.setDebug(True)

class TestConverter(TestCase):

    def test_run(self):
        filename = 'instance.mps'
        format = 'mpl'
        f = Path(filename)
        f.write_text('text')
        converter = Converter(filename, format)
        self.assertTrue(converter.run())

    def test_run_no_file(self):
        filename = 'instance_1.mps'
        format = 'mpl'
        converter = Converter(filename, format)
        with self.assertRaises(ValueError) as e:
            converter.run()
        self.assertEqual(str(e.exception), "Instance file not found.")

    def test_run_not_supported_in_format(self):
        filename = 'instance.trk'
        format = 'mpl'
        f = Path(filename)
        f.write_text('text')
        converter = Converter(filename, format)
        with self.assertRaises(ValueError) as e:
            converter.run()
        self.assertEqual(str(e.exception), "Input file format is not supported.")

    def test_run_not_supported_out_format(self):
        filename = 'instance_1.mps'
        format = 'trk'
        f = Path(filename)
        f.write_text('text')
        converter = Converter(filename, format)
        with self.assertRaises(ValueError) as e:
            converter.run()
        self.assertEqual(str(e.exception), "Output file format is not supported.")

    @classmethod
    def tearDownClass(cls):
        temp_files = ['instance.mps', 'instance.trk', 'instance_1.mps']
        for filename in temp_files:
            f = Path(filename)
            if f.is_file():
                f.unlink()


class TestModel(TestCase):

    def test__init__(self):
        Model()
        self.assertTrue(True)

class Test_command_line(TestCase):

    def test_parse_args(self):
        filename = 'instance.mps'
        fileformat = 'mpl'
        parsed = parse_args(['--file', filename, '--out_format', fileformat])
        self.assertEqual(parsed.file, filename)
        self.assertEqual(parsed.format, fileformat)

    def test_parse_args_no_filename(self):
        fileformat = 'mpl'
        parsed = parse_args(['--out_format', fileformat])
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
            parse_args(['--file', filename, '--out_format', fileformat])
        self.assertEqual(str(e.exception), "argument --format: invalid choice: 'trk' (choose from None, 'mpl', 'mps')")

    # input() will return 'yes' during this test
    @patch('builtins.input', return_value='y')
    def test_command_line(self, input):
        filename = 'instance.mps'
        format = 'mpl'
        f = Path(filename)
        f.write_text('text')
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertTrue(command_line())

    @classmethod
    def tearDownClass(cls):
        temp_files = ['instance.mps', 'instance.trk', 'instance_1.mps']
        for filename in temp_files:
            f = Path(filename)
            if f.is_file():
                f.unlink()