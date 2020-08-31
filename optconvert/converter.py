from pathlib import Path
from optconvert import Messages, Model

class Converter:

    debug = False

    def __init__(self, file: str, out_format: str, name=None):
        self.file = file
        self.in_format = Path(file).suffix[1:]
        self.out_format = out_format
        if name is None:
            name = Path(file).stem
        self.name = name


    def run(self):

        try:
            model = Model(Path(self.file))
            model.export(Path(f'{self.name}.{self.out_format}'))
        except Exception as e:
            raise e

        return True