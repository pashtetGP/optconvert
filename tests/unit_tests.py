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
        filename = 'Dakota_det.mps'
        format = 'mpl'
        converter = Converter(filename, format, 'Dakota_det_converted')
        self.assertTrue(converter.run())

    def test_run_no_file(self):
        filename = 'instance_1.mps'
        format = 'mpl'
        converter = Converter(filename, format)
        with self.assertRaises(FileNotFoundError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    def test_run_not_supported_in_format(self):
        filename = 'Dakota_det.trk'
        format = 'mpl'
        converter = Converter(filename, format)
        with self.assertRaises(ValueError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def test_run_not_supported_out_format(self):
        filename = 'Dakota_det.mps'
        format = 'trk'
        converter = Converter(filename, format)
        with self.assertRaises(ValueError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

    @classmethod
    def tearDownClass(cls):
        temp_files = []
        for filename in temp_files:
            f = Path(filename)
            if f.is_file():
                f.unlink()


class TestModel(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.initial_argv = sys.argv

    def test__init(self):
        filename = 'Dakota_det'
        for format in ['lp', 'mpl', 'mps']:
            model = Model(Path(f'{filename}.{format}'))
            self.assertEqual(abs(model.solve()), 4169.0)

    def test__init_wrong(self):
        filename = 'Dakota_det_wrong'
        format = 'mpl'
        with self.assertRaises(ModelResultException) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception)[:88], "The Model.ReadModel(filename='Dakota_det_wrong.mpl') method returned result='ParserError")

    def test__init_not_existing_file(self):
        filename = 'mps_instance_na'
        format = 'mps'
        with self.assertRaises(FileNotFoundError) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    def test__init_not_supported_in_file(self):
        filename = 'Dakota_det'
        format = 'trk'
        with self.assertRaises(ValueError) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def test__save(self):
        filename = 'Dakota_det'
        in_formats = ['mpl', 'mps', 'lp']
        out_formats = ['mpl', 'mps', 'lp']
        for in_format in in_formats:
            model = Model(Path(f'{filename}.{in_format}'))
            for out_format in out_formats:
                print(f'Testing In format: {in_format} Out format: {out_format}')
                model.save(out_format, f'{filename}_converted')
                model_new = Model(Path(f'{filename}_converted.{out_format}'))
                self.assertEqual(abs(model_new.solve()), 4169.0)

    def test_save_not_supported_out_format(self):
        filename = 'Dakota_det'
        format = 'mpl'
        out_format = 'trk'
        model = Model(Path(f'{filename}.{format}'))
        with self.assertRaises(ValueError) as e:
            model.save(format=out_format)
        self.assertEqual(str(e.exception), Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

    def test__save_stochastic(self):
        filename = 'SNDP_stochastic_MIP'
        in_format = 'mpl' # only mpl works for for stochastic, MPS does not work
        out_format = 'mps' # only mps out works
        model = Model(Path(f'{filename}.{in_format}'))
        print(f'Testing In format: {in_format} Out format: {out_format}')
        model.save(out_format, f'{filename}_converted')
        model_new = Model(Path(f'{filename}_converted.{out_format}'))
        self.assertEqual(model_new.solve(), -15250.0)

    def test__save_not_supported_out_stoch_format(self):
        self.assertTrue(False)

    @classmethod
    def tearDownClass(cls):
        for file in ['new_instance.lp', 'Dakota_det_converted.mpl', 'Dakota_det_converted.mps', 'Dakota_det_converted.lp', 'Dakota_det_converted_after_parse_file().mpl', 'Dakota_det_after_parse_file().mpl']:
            f = Path(file)
            if f.is_file():
                f.unlink()


class Test_command_line(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_files = []
        cls.initial_argv = sys.argv
        for file in cls.temp_files:
            f = Path(file)
            f.write_text('text')

    def test_parse_args(self):
        filename = 'mps_instance.mps'
        fileformat = 'sim'
        parsed = parse_args(['--file', filename, '--out_format', fileformat])
        self.assertEqual(parsed.files, [filename])
        self.assertEqual(parsed.out_format, fileformat)

    def test_parse_args_no_filename(self):
        fileformat = 'sim'
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
        filename = 'Dakota_det.mpl'
        format = 'sim'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertEqual(command_line(), Messages.MSG_FILE_CONVERTED)

    @patch('builtins.input', side_effect=['y'])
    def test_command_line_file_not_exists(self, input):
        filename = 'instance_na.mps'
        format = 'mpl'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertEqual(str(command_line()), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    @patch('builtins.input', side_effect=['n', 0, 'y'])
    def test_command_line_file_not_exists_ask_againe_answer_file(self, input):
        filename = 'instance_na.mps'
        format = 'sim'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertTrue(str(command_line()), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    @patch('builtins.input', side_effect=[100, 0, 'y'])
    def test_command_line_no_file_ask_againe_answer_wrong_index(self, input):
        format = 'sim'
        sys.argv = sys.argv + ['--out_format', format]
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=[4, 'y'])
    def test_command_line_no_file_ask_againe_answer_extension(self, input):
        format = 'sim'
        sys.argv = sys.argv + ['--out_format', format]
        self.assertTrue(4 >= len(self.temp_files)-2, msg='Second mocked value should choose extension.')
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=['y'])
    def test_command_line_not_supported_in_format(self, input):
        filename = 'Dakota_det.trk'
        format = 'sim'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertEqual(str(command_line()), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def tearDown(self):
        # reset command line arguments after every test
        sys.argv = Test_command_line.initial_argv

    @classmethod
    def tearDownClass(cls):
        for file in cls.temp_files + ['Dakota_det.sim', 'Dakota_det_after_parse_file().mpl']:
            f = Path(file)
            if f.is_file():
                f.unlink()