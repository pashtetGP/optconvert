from pathlib import Path

class Converter:

    supported_formats = ['mpl', 'mps']
    debug = False

    def __init__(self, file, format):
        self.file = file
        self.format = format

    @classmethod
    def setDebug(cls, debug: bool):
        print('Debug for converter set to True.')
        cls.debug = debug

    @classmethod
    def isDebug(cls):
        return cls.debug

    def run(self):

        if self.format == 'mpl':
            pass
        elif self.format == 'lp':
            pass
        else:
            raise ValueError('Output file format is not supported.')

        if Path(self.file).is_file():
            pass
        else:
            raise ValueError('File not found.')

        print(f'File{self.file} converted into format {self.format}.')
        return True

def main():
    pass