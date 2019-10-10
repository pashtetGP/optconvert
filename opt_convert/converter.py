from pathlib import Path
from opt_convert import Messages

class Converter:

    supported_out_formats = ['mpl', 'mps']
    supported_in_formats = ['mpl', 'mps']
    debug = False

    def __init__(self, file, out_format):
        self.file = file
        self.in_format = Path(file).suffix[1:]
        self.out_format = out_format

    @classmethod
    def setDebug(cls, debug: bool):
        print('Debug for converter set to True.')
        cls.debug = debug

    @classmethod
    def isDebug(cls):
        return cls.debug

    def run(self):

        if self.out_format not in Converter.supported_out_formats:
            raise ValueError(Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

        if not Path(self.file).is_file():
            raise ValueError(Messages.MSG_INSTANCE_FILE_NOT_FOUND)

        if self.in_format not in Converter.supported_in_formats:
            raise ValueError(Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

        # TODO: convert
        if Converter.isDebug():
            print(f'File {self.file} converted into format {self.out_format}.')

        return True

def main():
    pass