from pathlib import Path
import re
from opt_convert import Messages, Numbers
from mplpy import mpl, ResultType, ModelResultException

class Model:

    # smps means three files: cor, tim, sto
    supported_out_formats = ['mpl', 'mps', 'lp', 'smps']
    supported_in_formats = ['mpl', 'mps', 'lp']

    debug = False

    def __init__(self, file: Path):
        self.file = None # defined in read_file()
        self.format = None # defined in read_file()
        self.mpl_model = None  # defined in read_file()
        self.__read_file(file)

    def __read_file(self, file: Path):

        if self.file is not None:
            raise AttributeError(Messages.MSG_MODEL_READ_FILE_ONLY_ONCE)

        if not isinstance(file, Path):
            raise AttributeError(Messages.MSG_FILE_SHOULD_BE_PATH)

        self.file = file
        self.format = file.suffix[1:]

        if not self.file.is_file():
            raise FileNotFoundError(Messages.MSG_INSTANCE_FILE_NOT_FOUND)

        if not self.format in Model.supported_in_formats:
            raise ValueError(Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

        filename = str(self.file)
        if self.format in ['mpl', 'lp']: # for these formats we can create an mpl_model
            self.mpl_model = mpl.Models.Add(filename)
            try:
                if self.format in ['mpl']: # these formats can be nativaly read with mpl.Model.ReadModel()
                    result = self.mpl_model.ReadModel(filename)
                elif self.format in ['lp']: # these formats are first tansformed to mpl as text and then read by mpl.Model with ParseModel()
                    result = self.parse_file()
            except ModelResultException as e:
                raise e
            if result != ResultType.Success:
                raise ModelResultException(result.ErrorMessage)
        elif self.format == 'mps': # TODO: MPL can natively read mpl and mps files
            pass
        elif self.format == 'smps':
            pass
        else:
            assert(False and Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

        if self.isDebug():
            print(f'Read file {self.file}')

    def parse_file(self):

        if self.format == 'lp':
            mpl_string = self.parse_lp()
        else:
            raise ValueError(Messages.MSG_MODEL_NO_PARSING_FOR_FORMAT)

        return self.mpl_model.ParseModel(mpl_string)

    def parse_lp(self):
        # TODO: implement (for bounds)
        # TODO: this is cplex format
        # About CPLEX lp format: http://lpsolve.sourceforge.net/5.1/CPLEX-format.htm
        lp_string = self.file.read_text()
        lines = lp_string.split('\n')
        processed_lines = []
        counter = {'constraints': 0, 'not_free_bounds': 0}
        current_label = ''
        current_mpl_block = None
        vars = {'FREE': [], 'BINARY': [], 'INTEGER': []} # we do not need to track continuous vars
        final_comments = []
        infinity_substitution = False
        # MPL: [lp block names]
        blocks_dict = {'MAXIMIZE': ['MAXIMIZE', 'MAXIMUM', 'MAX'],
                       'MINIMIZE': ['MINIMIZE', 'MINIMUM', 'MIN'],
                       'SUBJECT TO': ['SUBJECT TO', 'SUCH THAT', 'ST', 'S.T.'],
                       'BOUNDS': ['BOUNDS', 'BOUND'],
                       'INTEGER': ['INTEGERS', 'GENERAL'],
                       'BINARY': ['BINARY']}
        for line in lines:

            # skip empty lines
            if len(line) == 0:
                continue

            # transform comments
            if line[0] == '\\':
                line = line.replace('\\', '! ', 1)
                processed_lines.append(line)
                continue

            updated_current_mpl_block = False
            for mpl_block in blocks_dict.keys():
                if any(lp_block == line.upper() for lp_block in blocks_dict[mpl_block]):
                    current_mpl_block = mpl_block
                    if current_mpl_block not in ['INTEGER', 'BINARY']: # these two will be added at the end before END
                        processed_lines.append(2 * '\n' + current_mpl_block + '\n')
                    updated_current_mpl_block = True
                    break
            else:
                if any(s == line.upper() for s in ['END']):

                    # append FREE, BINARY, INTEGER
                    for var_category in ['FREE', 'BINARY', 'INTEGER']:
                        if len(vars[var_category]): processed_lines.append(2*'\n' + var_category + '\n')
                        for variable in vars[var_category]:
                            processed_lines.append(variable + ';')

                    # append final comments
                    processed_lines.append('\n')
                    if infinity_substitution: final_comments.append('infinity was substituted with a big number in BOUNDS')
                    for comment in final_comments:
                        processed_lines.append(f'! {comment}')

                    processed_lines.append('\nEND')
                    updated_current_mpl_block = True

            if updated_current_mpl_block: continue

            if current_mpl_block in ['MAXIMIZE', 'MINIMIZE']:
                line = line.replace(': ', ' = ')
                processed_lines.append(line)
                continue
            elif current_mpl_block == 'SUBJECT TO':
                if current_label == '':
                    counter['constraints'] += 1
                    if ':' in line:
                        current_label = line.split(':')[0].strip()
                    else:
                        current_label = f"c{counter['constraints']}"
                        line = f"{current_label}: {line}"
                # Add ';' to constraints definition
                # "The right-hand side coefficient must be typed on the same line as the sense indicator. Acceptable sense indicators are <, <=, =<, >, >=, =>, and ='
                if any(sign in line for sign in ['<', '<=', '=<', '>', '>=', '=>', '=']):
                    line += ' ;'
                    current_label = ''
                processed_lines.append(line)
                continue
            elif current_mpl_block == 'BOUNDS':
                if ' FREE' in line.upper():
                    var_name = line.split()[0].strip()
                    vars['FREE'].append(var_name)
                    final_comments.append(f'FREE var {var_name} moved from BOUNDS in lp to FREE block in mpl')
                else:
                    counter['not_free_bounds'] += 1
                    # Substitute infinity with a big number
                    if any(s in line.lower() for s in ['+infinity', '+inf', '-infinity', '-inf']):
                        infinity_substitution = True
                        for word in ['infinity', 'inf']:
                            line = re.sub(word, str(Numbers.INT_BIG_NUMBER), line, flags=re.IGNORECASE)
                    processed_lines.append(line + ' ;')
                continue
            elif current_mpl_block in ['INTEGER', 'BINARY']:
                vars[current_mpl_block].append(line.strip())
                continue
            else:
                assert(False)

        mpl_string = ''.join([line + '\n' for line in processed_lines])

        if self.isDebug():
            f = Path(f'{self.file.stem}_after_parse_file().mpl')
            f.write_text(mpl_string)

        return mpl_string

    def save(self, format=None, name=None):

        if format == None:
            format = self.format
        if name == None:
            name = self.filename

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
