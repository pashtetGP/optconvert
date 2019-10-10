import argparse
import sys
from pathlib import Path
from opt_convert import Converter, Messages, Model

def parse_args(args):

    supported_formats = Model.supported_out_formats

    parser = argparse.ArgumentParser(prog='opt_convert',
                                     description='opt_convert converts files of (stochastic) optimization instances.')

    parser.add_argument('--file', default=[], type=str, action='append', dest='files',
                        help="Filename with the extension of the file to convert, e.g., siplib.lp. Default value: None (chose files interactively)")
    parser.add_argument('--out_format', default=None, choices=[None] + supported_formats,
                        help=f"Output format: {', '.join(supported_formats)}. Default value: None (choose format interactively)")

    return parser.parse_args(args)

def command_line():

    '''

    :return: True - no errors happend during the conversion, or the last Error during the conversion.
    '''

    cwd = Path(__file__).cwd()

    # parser will check the validity of out_format parameter
    parsed = parse_args(sys.argv[1:])
    files = parsed.files
    out_format = parsed.out_format

    result = False  # for testing
    quit = False
    while not quit:

        if not files:

            supported_files = []
            for ext in Model.supported_in_formats:
                pathes = cwd.glob(f'*.{ext}')
                supported_files.extend([path.relative_to(cwd) for path in pathes])

            n_supported_files = len(supported_files)
            files_by_ext = {key: [] for key in Model.supported_in_formats}
            for i, file in enumerate(supported_files):
                print(f'{i} - {file}')
                file_ext = file.suffix[1:]
                files_by_ext[file_ext].append(file)
            for ext, instances in files_by_ext.items():
                if instances:
                    i = i+1
                    supported_files.append(ext)
                    print(f'{i} - {ext}')

            while not files:
                answer = input('Please choose the file or extension: ')
                try:
                    if answer < n_supported_files: # choose a specific file
                        files.append(supported_files[answer])
                    else: # choose an extension
                        ext = supported_files[answer]
                        files = files_by_ext[ext]
                except:
                    print(Messages.MSG_INPUT_WRONG_INDEX)
            # TODO: list of extensions

        if out_format is None:

            for i, format in enumerate(Model.supported_out_formats):
                print(f'{i} - {format}')

            while out_format is None:
                answer = input('Please choose the output format: ')
                try:
                    out_format = Model.supported_out_formats[answer]
                except:
                    print(Messages.MSG_INPUT_WRONG_INDEX)

        result = True
        for file in files:
            converter = Converter(file, out_format)
            try:
                converter.run()
            except FileNotFoundError as e:
                result = e
                print(file, e)
                if str(e) == Messages.MSG_INSTANCE_FILE_NOT_FOUND:
                    # reset file info to choose it interactively later
                    files = []
            except ValueError as e:
                result = e
                print(file, e)
                if e == Messages.MSG_OUT_FORMAT_NOT_SUPPORTED:
                    # reset format info to choose it interactively later
                    out_format = None
            else:
                # reset all
                files = []
                out_format = None

        answer = input('Exit (y/n)? ')
        if answer == 'y':
            quit = True

    return result