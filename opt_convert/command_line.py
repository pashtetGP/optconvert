import argparse
import sys
# from opt_convert import Converter

def parse_args(args):

    supported_formats = Converter.supported_formats

    parser = argparse.ArgumentParser(prog='opt_convert',
                                     description='opt_convert converts files of (stochastic) optimization instances.')

    parser.add_argument('--file', default=None, type=str,
                        help="Filename with the extension of the file to convert, e.g., siplib.lp. Default value: None (chose files interactively)")
    parser.add_argument('--format', default=None, choices=[None] + supported_formats,
                        help=f"Output format: {', '.join(supported_formats)}. Default value: None (chose format interactively)")

    return parser.parse_args(args)

def command_line():

    parsed = parse_args(sys.argv[1:])
    if parsed.file is not None:
        pass
    else:
        pass
        # choose file

    # if both arguments specified
    # if first arguments specified
    # if second argument specified
    # if none arguments specified
    print(parsed)