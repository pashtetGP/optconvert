from unittest import TestCase
from unittest.mock import patch
import sys
from opt_convert import Converter, Model, parse_args, command_line, Messages
from argparse import ArgumentError
from pathlib import Path

Converter.setDebug(True)

class TestConverter(TestCase):

    def test_run(self):
        filename = 'mps_instance.mps'
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
        temp_files = ['mps_instance.mps', 'instance.trk', 'instance_1.mps']
        for filename in temp_files:
            f = Path(filename)
            if f.is_file():
                f.unlink()


class TestModel(TestCase):

    def test__init__(self):
        Model()
        self.assertTrue(True)

class Test_command_line(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_files = ['mps_instance.mps', 'instance.trk', 'mpl_instance.mpl', 'lp_instance.lp', 'mps_instance_2.mps']
        cls.initial_argv = sys.argv
        for file in cls.temp_files:
            f = Path(file)
            f.write_text('text')

    def test_parse_args(self):
        filename = 'mps_instance.mps'
        fileformat = 'mpl'
        parsed = parse_args(['--file', filename, '--out_format', fileformat])
        self.assertEqual(parsed.files, [filename])
        self.assertEqual(parsed.out_format, fileformat)

    def test_parse_args_no_filename(self):
        fileformat = 'mpl'
        parsed = parse_args(['--out_format', fileformat])
        self.assertEqual(parsed.files, [])
        self.assertEqual(parsed.out_format, fileformat)

    def test_parse_args_no_fileformat(self):
        filename = 'mps_instance.mps'
        parsed = parse_args(['--file', filename])
        self.assertEqual(parsed.files, [filename])
        self.assertIs(parsed.out_format, None)

    def test_parse_args_none(self):
        parsed = parse_args([])
        self.assertEqual(parsed.files, [])
        self.assertIs(parsed.out_format, None)

    @patch('builtins.input', side_effect=['y'])
    def test_command_line(self, input):
        filename = 'mps_instance.mps'
        format = 'mpl'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=['y'])
    def test_command_line_file_not_exists(self, input):
        filename = 'instance_na.mps'
        format = 'mpl'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertEqual(str(command_line()), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    @patch('builtins.input', side_effect=['n', 0, 'y'])
    def test_command_line_file_not_exists_ask_againe_answer_file(self, input):
        filename = 'instance_na.mps'
        format = 'mpl'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=[100, 0, 'y'])
    def test_command_line_no_file_ask_againe_answer_wrong_index(self, input):
        format = 'mpl'
        sys.argv = sys.argv + ['--out_format', format]
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=[4, 'y'])
    def test_command_line_no_file_ask_againe_answer_extension(self, input):
        format = 'mpl'
        sys.argv = sys.argv + ['--out_format', format]
        self.assertTrue(4 >= len(self.temp_files)-2, msg='Second mocked value should choose extension.')
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=['y'])
    def test_command_line_not_supported_in_format(self, input):
        filename = 'instance.trk'
        format = 'mpl'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertEqual(str(command_line()), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def tearDown(self):
        # reset command line arguments after every test
        sys.argv = Test_command_line.initial_argv

    @classmethod
    def tearDownClass(cls):
        for file in cls.temp_files:
            f = Path(file)
            if f.is_file():
                f.unlink()