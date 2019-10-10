from pathlib import Path
from opt_convert import Messages

class Model:

    supported_out_formats = ['mpl', 'mps', 'lp']
    supported_in_formats = ['mpl', 'mps']

    debug = False

    def __init__(self, file: Path):
        self.file = None # defined in read_file()
        self.name = None # defined in read_file()
        self.format = None # defined in read_file()
        self.mpl_model = None  # defined in read_file()
        self.__read_file(file)

    def __read_file(self, file: Path):

        if self.file is not None:
            raise AttributeError(Messages.MSG_MODEL_READ_FILE_ONLY_ONCE)

        if not isinstance(file, Path):
            raise AttributeError(Messages.MSG_FILE_SHOULD_BE_PATH)

        self.file = file
        self.name = file.stem
        self.format = file.suffix[1:]

        if not self.file.is_file():
            raise FileNotFoundError(Messages.MSG_INSTANCE_FILE_NOT_FOUND)

        if not self.format in Model.supported_in_formats:
            raise ValueError(Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

        # READ FILE
        self.mpl_model = 'smth'

        if self.isDebug():
            print(f'Read file {self.file}')

    def save(self, format=None, name=None):

        if format == None:
            format = self.format
        if name == None:
            name = self.name

        if not format in Model.supported_out_formats:
            raise ValueError(Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

        # save_model
        if self.isDebug():
            print(f'Saved file {name}.{format}')

        return True

    @classmethod
    def setDebug(cls, debug: bool):
        print('Debug for Model set to True.')
        cls.debug = debug

    @classmethod
    def isDebug(cls):
        return cls.debug
