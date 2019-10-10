from pathlib import Path
from opt_convert import Messages, Model

class Converter:

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

        if Converter.isDebug():
            Model.setDebug(True)

        try:
            model = Model(Path(self.file))
            model.save(self.out_format)
        except Exception as e:
            raise e

        if Converter.isDebug():
            print(f'File {self.file} converted into format {self.out_format}.')

        return True

def main():
    pass