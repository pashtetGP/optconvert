from unittest import TestCase
from unittest.mock import patch
from mplpy import ModelResultException
import sys
from pathlib import Path
from opt_convert import Converter, Model, parse_args, command_line, Messages, Numbers

Converter.setDebug(True)
Model.setDebug(True)

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
        with self.assertRaises(FileNotFoundError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    def test_run_not_supported_in_format(self):
        filename = 'instance.trk'
        format = 'mpl'
        f = Path(filename)
        f.write_text('text')
        converter = Converter(filename, format)
        with self.assertRaises(ValueError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def test_run_not_supported_out_format(self):
        filename = 'instance_1.mps'
        format = 'trk'
        f = Path(filename)
        f.write_text('text')
        converter = Converter(filename, format)
        with self.assertRaises(ValueError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

    @classmethod
    def tearDownClass(cls):
        temp_files = ['mps_instance.mps', 'instance.trk', 'instance_1.mps']
        for filename in temp_files:
            f = Path(filename)
            if f.is_file():
                f.unlink()


class TestModel(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_files = ['mps_instance.mps', 'instance.trk', 'mpl_instance.mpl', 'lp_instance.lp', 'mps_instance_2.mps']
        cls.initial_argv = sys.argv
        for file in cls.temp_files:
            f = Path(file)
            f.write_text('text')

    def test__init_mpl(self):
        filename = 'Dakota_det'
        format = 'mpl'
        model = Model(Path(f'{filename}.{format}'))
        self.assertEqual(model.file.stem, filename)

    def test__init_mpl_wrong(self):
        filename = 'Dakota_det_wrong'
        format = 'mpl'
        with self.assertRaises(ModelResultException) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception)[:88], "The Model.ReadModel(filename='Dakota_det_wrong.mpl') method returned result='ParserError")

    def test__init_lp(self):
        filename = 'Dakota_det'
        format = 'lp'
        model = Model(Path(f'{filename}.{format}'))
        self.assertEqual(model.file.stem, filename)

    def test__init_not_existing_file(self):
        filename = 'mps_instance_na'
        format = 'mps'
        with self.assertRaises(FileNotFoundError) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    def test__init_not_supported_in_file(self):
        filename = 'instance'
        format = 'trk'
        with self.assertRaises(ValueError) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def test__save(self):
        filename = 'mps_instance'
        format = 'mps'
        model = Model(Path(f'{filename}.{format}'))
        self.assertTrue(model.save())

    def test__save_another_file_and_format(self):
        filename = 'mps_instance'
        format = 'mps'
        model = Model(Path(f'{filename}.{format}'))
        self.assertTrue(model.save('lp', 'new_instances'))

    def test_save_not_supported_out_format(self):
        filename = 'mps_instance'
        format = 'mps'
        out_format = 'trk'
        model = Model(Path(f'{filename}.{format}'))
        with self.assertRaises(ValueError) as e:
            model.save(format=out_format)
        self.assertEqual(str(e.exception), Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

    @classmethod
    def tearDownClass(cls):
        for file in cls.temp_files + ['new_instance.lp']:
            f = Path(file)
            if f.is_file():
                f.unlink()


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