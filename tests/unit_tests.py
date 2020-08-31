from unittest import TestCase, TestLoader, TextTestRunner, skip
from unittest.mock import patch
import sys
from pathlib import Path
import shutil
from optconvert import Converter, Model, MplWithExtData, parse_args, command_line, Messages, Solvers


class TestConverter(TestCase):

    def test_run(self):
        filename = 'Dakota_det.mps'
        format = 'mpl'
        converter = Converter(filename, format, 'Dakota_det_converted')
        self.assertTrue(converter.run())

    def test_run_CAP(self):
        filename = 'cap_test_5.mpl'
        format = 'mps'
        converter = Converter(filename, format, 'cap_test_5')
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
        with self.assertRaises(RuntimeError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def test_run_not_supported_out_format(self):
        filename = 'Dakota_det.mps'
        format = 'trk'
        converter = Converter(filename, format)
        with self.assertRaises(RuntimeError) as e:
            converter.run()
        self.assertEqual(str(e.exception), Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

    @classmethod
    def tearDownClass(cls):
        temp_files = ['Dakota_det_converted.mpl', 'cap_test_5.cor', 'cap_test_5.STO', 'cap_test_5.TIM']
        for filename in temp_files:
            f = Path(filename)
            if f.is_file():
                f.unlink()


class TestModel(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.initial_argv = sys.argv
        cls.dakota_det_solution = -4169.0
        Path('temp_subfolder').mkdir(parents=True, exist_ok=True)

    def test_init(self):
        filename = 'Dakota_det'
        for format in ['lp', 'mpl', 'mps']:
            model = Model(Path(f'{filename}.{format}'))
            self.assertAlmostEqual(model.solve(), -4169.0, 3)

    def test_init_wrong(self):
        filename = 'Dakota_det_wrong'
        format = 'mpl'
        with self.assertRaises(RuntimeError) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception)[:88], "The Model.ReadModel(filename='Dakota_det_wrong.mpl') method returned result='ParserError")

    def test_init_not_existing_file(self):
        filename = 'mps_instance_na'
        format = 'mps'
        with self.assertRaises(FileNotFoundError) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    def test_init_not_supported_in_file(self):
        filename = 'Dakota_det'
        format = 'trk'
        with self.assertRaises(RuntimeError) as e:
            Model(Path(f'{filename}.{format}'))
        self.assertEqual(str(e.exception), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def test_solve_default(self):
        filename = 'Dakota_det'
        for format in ['lp', 'mpl', 'mps']:
            model = Model(Path(f'{filename}.{format}'))
            self.assertAlmostEqual(model.solve(), self.dakota_det_solution, 3)

    def test_solve_lpsolve(self):
        filename = 'Dakota_det'
        for format in ['lp', 'mpl', 'mps']:
            model = Model(Path(f'{filename}.{format}'))
            self.assertAlmostEqual(model.solve(Solvers.LPSOLVE), self.dakota_det_solution, 3)

    def test_export(self):
        filename = 'Dakota_det'
        in_formats = ['mpl', 'mps', 'lp']
        out_formats = ['mpl', 'mps', 'lp']
        for in_format in in_formats:
            model = Model(Path(f'{filename}.{in_format}'))
            for out_format in out_formats:
                print(f'Testing In format: {in_format} Out format: {out_format}')
                model.export(Path(f'{filename}_converted.{out_format}'))
                model_new = Model(Path(f'{filename}_converted.{out_format}'))
                self.assertAlmostEqual(model_new.solve(), self.dakota_det_solution, 3)

    def test_export_subfolder(self):
        filename = 'Dakota_det'
        out_file = 'temp_subfolder//Dakota_det'
        in_formats = ['mpl', 'mps', 'lp']
        out_formats = ['mpl', 'mps', 'lp']
        for in_format in in_formats:
            model = Model(Path(f'{filename}.{in_format}'))
            for out_format in out_formats:
                print(f'Testing In format: {in_format} Out format: {out_format}')
                model.export(Path(f'{out_file}_converted.{out_format}'))
                model_new = Model(Path(f'{out_file}_converted.{out_format}'))
                self.assertAlmostEqual(model_new.solve(), self.dakota_det_solution, 3)

    def test_export_not_supported_out_format(self):
        filename = 'Dakota_det'
        format = 'mpl'
        out_format = 'trk'
        model = Model(Path(f'{filename}.{format}'))
        with self.assertRaises(RuntimeError) as e:
            model.export(Path(f'{filename}_unsupported.{out_format}'))
        self.assertEqual(str(e.exception), Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

    def test_export_stochastic_mpl(self):
        filename = 'SNDP_stochastic_MIP'
        in_format = 'mpl'
        out_format = 'mps' # only mps out works
        model = Model(Path(f'{filename}.{in_format}'))
        model.export(Path(f'{filename}_converted.{out_format}'))

    def test_export_stochastic_mps(self):
        filename = 'SNDP_stochastic_MIP'
        in_format = 'mps'
        out_format = 'mps' # only mps out works
        model = Model(Path(f'{filename}.{in_format}'))
        model.export(Path(f'{filename}_converted.{out_format}'))

    def test_export_not_supported_out_stoch_format(self):
        filename = 'SNDP_stochastic_MIP'
        format = 'mpl'
        out_format = 'lp'
        model = Model(Path(f'{filename}.{format}'))
        with self.assertRaises(RuntimeError) as e:
            model.export(Path(f'{filename}_unsupported.{out_format}'))
        self.assertEqual(str(e.exception), Messages.MSG_STOCH_ONLY_TO_MPS)

    @classmethod
    def tearDownClass(cls):
        for file in ['new_instance.lp', 'Dakota_det_converted.mpl', 'Dakota_det_converted.mps', 'Dakota_det_converted.lp',
                     'Dakota_det_converted_after_parse_file().mpl', 'Dakota_det_after_parse_file().mpl',
                     'SNDP_stochastic_MIP_converted.cor', 'SNDP_stochastic_MIP_converted.sto', 'SNDP_stochastic_MIP_converted.tim']:
            f = Path(file)
            if f.is_file():
                f.unlink()
        shutil.rmtree('temp_subfolder')


class TestMplWithExtData(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sndp_default_solution = 2200

    def test_init(self):
        filename = 'SNDP_default.mpl'
        model = MplWithExtData(Path(filename))

    def test_set_ext_data(self):
        filename = 'SNDP_default.mpl'
        old_data = {'NrOfScen': 3,
                    'Prob': [{'SCEN': 1, 'value': 0.25}, {'SCEN': 2, 'value': 0.5}, {'SCEN': 3, 'value': 0.25}],
                    'Demand': [{'SCEN': 1, 'value': 2000}, {'SCEN': 2, 'value': 5000}, {'SCEN': 3, 'value': 8000}]}
        new_data = {'NrOfScen': 1,
                    'Prob': [{'SCEN': 1, 'value': 1}],
                    'Demand': [{'SCEN': 1, 'value': 1050}]}
        model = MplWithExtData(Path(filename))
        model.set_ext_data(new_data)
        solution = model.solve()
        model.set_ext_data(old_data)
        self.assertAlmostEqual(self.sndp_default_solution, solution, delta=0.01)

    def test_export(self):
        filename = 'SNDP_default.mpl'
        old_data = {'NrOfScen': 3,
                    'Prob': [{'SCEN': 1, 'value': 0.25}, {'SCEN': 2, 'value': 0.5}, {'SCEN': 3, 'value': 0.25}],
                    'Demand': [{'SCEN': 1, 'value': 2000}, {'SCEN': 2, 'value': 5000}, {'SCEN': 3, 'value': 8000}]}
        new_data = {'NrOfScen': 1,
                    'Prob': [{'SCEN': 1, 'value': 1}],
                    'Demand': [{'SCEN': 1, 'value': 1050}]}
        model = MplWithExtData(Path(filename))
        model.set_ext_data(new_data)
        model.export(Path('SNDP_one_scen.mpl'))
        model.export(Path('SNDP_one_scen.mps'))
        model.set_ext_data(old_data)

        one_scen_model = MplWithExtData(Path('SNDP_one_scen.mpl'))
        solution = one_scen_model.solve()
        self.assertAlmostEqual(self.sndp_default_solution, solution, delta=0.01)

    @classmethod
    def tearDownClass(cls):
        for file in Path().glob("SNDP_one_scen*"):
            file.unlink()


class TestCommandLine(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_files = ['Dakota_det.sim', 'Dakota_det_after_parse_file().mpl',
                       'SNDP_stochastic_MIP.cor', 'SNDP_stochastic_MIP.tim', 'SNDP_stochastic_MIP.sto']
        cls.initial_argv = sys.argv

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

    @skip
    def test_command_line_manual_enter(self):
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=['y'])
    def test_command_line(self, input):
        filename = 'Dakota_det.mpl'
        format = 'sim'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=['y'])
    def test_command_line_file_not_exists(self, input):
        filename = 'instance_na.mps'
        format = 'mpl'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertEqual(str(command_line()), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    @patch('builtins.input', side_effect=['n', '0', 'exit'])
    def test_command_line_file_not_exists_ask_againe_answer_file(self, input):
        filename = 'instance_na.mps'
        format = 'sim'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertTrue(str(command_line()), Messages.MSG_INSTANCE_FILE_NOT_FOUND)

    @patch('builtins.input', side_effect=['100', '0', 'y'])
    def test_command_line_no_file_ask_againe_answer_wrong_index(self, input):
        format = 'sim'
        sys.argv = sys.argv + ['--out_format', format]
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=['7', 'y'])
    def test_command_line_no_file_ask_againe_answer_extension(self, input):
        format = 'sim'
        sys.argv = sys.argv + ['--out_format', format]
        self.assertTrue(command_line())

    @patch('builtins.input', side_effect=['y'])
    def test_command_line_not_supported_in_format(self, input):
        filename = 'Dakota_det.trk'
        format = 'sim'
        sys.argv = sys.argv + ['--file', filename, '--out_format', format]
        self.assertEqual(str(command_line()), Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

    def tearDown(self):
        # reset command line arguments after every test
        sys.argv = self.initial_argv

    @classmethod
    def tearDownClass(cls):
        for file in cls.temp_files:
            f = Path(file)
            if f.is_file():
                f.unlink()


if __name__ == '__main__':
    loader = TestLoader()
    suite = loader.discover('')
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)