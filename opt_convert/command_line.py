import argparse
import sys
from opt_convert import Converter, Messages

def parse_args(args):

    supported_formats = Converter.supported_out_formats

    parser = argparse.ArgumentParser(prog='opt_convert',
                                     description='opt_convert converts files of (stochastic) optimization instances.')

    parser.add_argument('--file', default=None, type=str,
                        help="Filename with the extension of the file to convert, e.g., siplib.lp. Default value: None (chose files interactively)")
    parser.add_argument('--out_format', default=None, choices=[None] + supported_formats,
                        help=f"Output format: {', '.join(supported_formats)}. Default value: None (choose format interactively)")

    return parser.parse_args(args)

def command_line():

    parsed = parse_args(sys.argv[1:])

    quit = False
    while not quit:

        if parsed.file is not None:
            file = parsed.file
        else:
            file = 1
            # choose file
            # list of files
            # list of extensions

        if parsed.out_format is not None:
            out_format = parsed.out_format
        else:
            out_format = 1
            # provide list of formats

        converter = Converter(file, out_format)
        try:
            converter.run()
        except ValueError as e:
            print(e)
            if e == Messages.MSG_INSTANCE_FILE_NOT_FOUND or e == Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED:
                # reset file info to choose it interactively later
                parsed.file = None
            elif e == Messages.MSG_OUT_FORMAT_NOT_SUPPORTED:
                # reset format info to choose it interactively later
                parsed.out_format = None

        answer = input('Exit (y/n)? ')
        if answer == 'y':
            quit = True

    return True