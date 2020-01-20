from pathlib import Path
import shutil
import re
from opt_convert import Messages, Numbers, InputFormatNotSupportedError, ExplicitInMpsError, OutFormatNotSupported
from mplpy import mpl, ResultType, ModelResultException, InputFileType
# TODO: continue line 245

mpl.Options['MpsCreateAsMin'].Value = 1  # always transform the obj function to min before mps gen
mpl.Options['MpsIntMarkers'].Value = 1  # use integer markers (instead of UI bound entries)

class Model:

    # smps means three files: cor, tim, sto
    # stochastic .mpl can be -> .sto, .cor, .tim only
    # stochastic .mps can be -> .sto, .cor, .tim only
    # .sto, .cor, .tim cannot be transformed
    supported_in_formats = ['mpl', 'mps', 'lp']
    supported_out_formats = ['mps', 'lp', 'xa', 'sim', 'mpl', 'gms', 'mod', 'xml', 'mat', 'c']

    compatible_with_PNB = True

    debug = False

    def __init__(self, file: Path):
        self.file = None # assigned in read_file()
        self.format = None # assigned in read_file()
        self.mpl_model = None  # assigned in read_file()
        self.stochastic = None # assigned in read_file()
        self._read_file(file)
        self.obj_value = None # assigned after solve()

    def _read_file(self, file: Path):

        if self.file is not None:
            raise RuntimeError(Messages.MSG_MODEL_READ_FILE_ONLY_ONCE)

        if not isinstance(file, Path):
            raise ValueError(Messages.MSG_FILE_SHOULD_BE_PATH)

        self.file = file
        self.format = file.suffix[1:]

        if not self.file.is_file():
            raise FileNotFoundError(Messages.MSG_INSTANCE_FILE_NOT_FOUND)

        if not self.format in Model.supported_in_formats:
            raise InputFormatNotSupportedError(Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

        filename = str(self.file)

        if self.format == 'mps':
            text = self.file.read_text()
            lines = text.split('\n')
            n_stoch_keywords = 0
            for line in lines:
                if any(keyword in line for keyword in ['STOCH', 'TIME', 'SCENARIOS']):
                    n_stoch_keywords += 1
                if n_stoch_keywords >= 3:
                    self.stochastic = True
                    return

        try:
            if self.format in ['mpl', 'mps']: # these formats can be natively read with mpl.Model.ReadModel()
                self.mpl_model = mpl.Models.Add(filename)
                self.mpl_model.ReadModel(filename)
            elif self.format in ['lp']: # these formats are first tansformed to mpl as text and then read by mpl.Model with ParseModel()
                self._parse_file()
        except ModelResultException as e:
            raise RuntimeError(e)

        if self.mpl_model.Matrix.ConStageCount:
            self.stochastic = True

        if self.isDebug():
            print(f'Read file {self.file}')

    def _parse_file(self):

        if self.format == 'lp':
            mpl_string = self._parse_lp()
        else:
            raise ValueError(Messages.MSG_MODEL_NO_PARSING_FOR_FORMAT)

        self.mpl_model = mpl.Models.Add(str(self.file))
        return self.mpl_model.ParseModel(mpl_string)

    def _parse_lp(self):
        # This is cplex format
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
                       'BINARY': ['BINARY', 'BINARIES']}
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

    def _mps2three(self, temp_file, filename):
        lines_in_files = {'cor': [], 'tim': [], 'sto': []}
        text = Path(temp_file).read_text()
        lines = text.split('\n')

        current_file_lines = 'cor'
        for line in lines:
            if current_file_lines == 'cor' and 'TIME' in line: # TIME block should go after COR
                current_file_lines = 'tim'
            elif current_file_lines == 'tim' and 'STOCH' in line:  # STOCH block should go after TIME
                current_file_lines = 'sto'
            elif 'EXPLICIT' in line and Model.compatible_with_PNB and current_file_lines == 'sto':
                raise ExplicitInMpsError(Messages.MSG_EXPLICIT_IN_MPS)

            lines_in_files[current_file_lines].append(line)

        for extension in ['cor', 'tim', 'sto']:
            contents = lines_in_files[extension]
            if extension in ['cor', 'tim']:
                contents.append('ENDATA')

            file = Path(f'{filename}.{extension}')
            file.write_text('\n'.join(contents))

        # Delete the file
        Path(temp_file).unlink()

    def save(self, format=None, name=None):

        format_dict = {
            'mps': InputFileType.Mps,
            'lp': InputFileType.Cplex,
            'xa': InputFileType.Xa,
            'sim': InputFileType.TSimplex,
            'mpl': InputFileType.Mpl,
            'gms': InputFileType.Gams,
            'mod': InputFileType.Ampl,
            'xml': InputFileType.OptML,
            'mat': InputFileType.Matlab,
            'c': InputFileType.CDef
        }

        if format == None:
            format = self.format
        if name == None:
            name = self.file.stem
        filename = f'{name}.{format}'

        if not format in Model.supported_out_formats:
            raise OutFormatNotSupported(Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

        if self.stochastic:
            if format not in ['mps']:
                raise RuntimeError(Messages.MSG_STOCH_ONLY_TO_MPS)
            elif self.format == 'mpl':
                self.mpl_model.WriteInputFile(str(self.file.stem)+'_temp', format_dict['mps']) # save temp .mps file
            elif self.format == 'mps':
                shutil.copy(str(self.file), str(self.file.stem)+'_temp.mps')
            self._mps2three(str(self.file.stem) + '_temp.mps', name)
        elif not self.mpl_model:
            raise RuntimeError(Messages.MSG_NO_MPL_MODEL_CANNOT_SAVE)
        else:
            self.mpl_model.WriteInputFile(filename, format_dict[format])

        # Bug in MPL with binary vars (added to INTEGERS block)
        if format == 'lp':
            lines = Path(filename).read_text().splitlines()
            processed_lines = []
            vector_bins = []
            for vector in self.mpl_model.VariableVectors: # vector.Type is often None (not set) and can't be used
                vector_bins.extend([var.Name for var in vector if var.IsBinary])
            plain_bins = [var.Name for var in self.mpl_model.PlainVariables if var.IsBinary]
            bin_vars = vector_bins + plain_bins
            if bin_vars:
                end_line_index = None
                for line in lines:
                    if 'END' == line.strip().upper():
                        end_line_index = len(processed_lines)
                    if not any([var_name == line.strip() for var_name in bin_vars]):
                        processed_lines.append(line)
                processed_lines.insert(end_line_index, 'BINARY')
                for i, var in enumerate(bin_vars, 1):
                    processed_lines.insert(end_line_index + i, var)
                processed_lines.insert(end_line_index + i + 1, '') # blank line after BINARY block
                Path(filename).write_text('\n'.join(processed_lines))

        if self.isDebug():
            if self.stochastic and format == 'mps':
                print(f'Saved files {name}.cor, .sto, .tim')
            else:
                print(f'Saved file {name}.{format}')

        return True

    def solve(self):

        if self.mpl_model:
            self.mpl_model.Solve()
            self.obj_value = self.mpl_model.Solution.ObjectValue
            return self.obj_value
        else:
            raise RuntimeError(Messages.MSG_NO_MPL_MODEL_CANNOT_SOLVE)

    @classmethod
    def setDebug(cls, debug: bool):
        print('Debug for Model set to True.')
        cls.debug = debug

    @classmethod
    def isDebug(cls):
        return cls.debug
