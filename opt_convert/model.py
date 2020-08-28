from pathlib import Path
import os
import shutil
import re
from opt_convert import Messages, Numbers
from mplpy import mpl, ResultType, ModelResultException, InputFileType

mpl.Options['MpsCreateAsMin'].Value = 1  # always transform the obj function to min before mps gen
mpl.Options['MpsIntMarkers'].Value = 0  # use UI bound entries (instead of integer markers), otherwise, BUG: all ints/bins are assigned to the 1st stage and all integers w/o UB are considered to be bins in SmiScnData
mpl.Options['MpsDefUIBound'].Value = Numbers.INT_BIG_NUMBER # UB to use for int var with inf UB


class Model:
    """
    A wrapper for MPL Model that enables model read / write / solve and convertion.

    Attributes
    ----------
    format : str
        an initial file extension of the model: mps, lp, xa, sim, mpl, gms, mod, xml, mat or c
    obj_value : float
        optimal objective value. Defined after Solve() call. Call it if Solve() was never called
    is_stochastic : bool
        is True if model is stochastic
    data_as_dict : dict
        returns model data in dict format. Not implemented. See MplWithExtData set_ext_data() for format and SndpGraph()

    Methods
    -------
    export(file=None)
        Converts the model and saves to file. File extensions defines the output format.
    solve
        Solves the model and returns the objective value

    Private Attributes
    -------
    _file : Path
        path to the file from which model was loaded. For some formats the model formulation is first loaded to memory and then passed to MPL
    _mpl_model : MPL Model
        intrinsic model

    Private Methods
    -------
    _read_file(file)
        guts of initialization that reads the file and loads it to MPL model
    _parse_file(file)
        called from _read_file() if necessary. Loads file contents to memory, processes it and loads to MPL model
    _read_lp(file)
        _parse_file() for LP
    _mps2three(temp_file, filename)
        creates three files .cor, .sto, .tim from .mps temp_file. The later is deleted

    Examples
    -------
    from opt_convert import Model
    from pathlib import Path

    in_file = Path('Dakota_det.mpl')
    model = Model(in_file)
    print('Solution: ' + str(model.solve()))
    out_file = in_file.with_suffix('lp')
    model.export(out_file)
    """

    supported_in_formats = ['mpl', 'mps', 'lp']
    supported_out_formats = ['mps', 'lp', 'xa', 'sim', 'mpl', 'gms', 'mod', 'xml', 'mat', 'c']

    def __init__(self, file: Path):
        self._file = None # assigned in read_file()
        self._mpl_model = None  # assigned in read_file()
        self._read_file(file)

    @property
    def format(self):
        return self._file.suffix[1:]

    @property
    def obj_value(self):
        solution = self._mpl_model.Solution
        if not solution.IsAvailable:
            self.solve()
        return self._mpl_model.Solution.ObjectValue

    @property
    def is_stochastic(self):
        if self._mpl_model.Matrix.ConStageCount:
            return True
        if self.format == 'mps':
            text = self._file.read_text()
            lines = text.split('\n')
            n_stoch_keywords = 0
            for line in lines:
                if any(keyword in line for keyword in ['STOCH', 'TIME', 'SCENARIOS']):
                    n_stoch_keywords += 1
                if n_stoch_keywords >= 3:
                    return True

    @property
    def data_as_dict(self):
        raise NotImplementedError() # see MplWithExtData set_ext_data() for format and SndpGraph()

    def export(self, file: Path = None):
        """Exports, i.e., saves the model into the file.
        Output file extension defines the output model format.
        smps means three files: .cor, .tim, .sto
        Stochastic .mpl can be transformed to .sto, .cor, .tim only
        Stochastic .mps can be transformed to .sto, .cor, .tim only
        .sto, .cor, .tim cannot be transformed

        Parameters
        ----------
        file : Path
            the output file

        Returns
        -------
        None
        """


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

        if file == None:
            format = self.format
            name = self._file.stem
        else:
            format = file.suffix[1:]
            name = file.stem

        if not format in Model.supported_out_formats:
            raise RuntimeError(Messages.MSG_OUT_FORMAT_NOT_SUPPORTED)

        if self.is_stochastic:
            temp_file = Path(str(self._file.stem) + '_temp.mps')
            if format not in ['mps']:
                raise RuntimeError(Messages.MSG_STOCH_ONLY_TO_MPS)
            elif self.format == 'mpl':
                self._mpl_model.WriteInputFile(str(self._file.stem) + '_temp', format_dict['mps']) # export temp .mps file
            elif self.format == 'mps': # stochastic mps is not parsed as mpl_model bust still can be converted
                shutil.copy(self._file, temp_file)
            self._mps2three(temp_file, name)
        elif not self._mpl_model:
            raise RuntimeError(Messages.MSG_NO_MPL_MODEL_CANNOT_SAVE)
        else:
            self._mpl_model.WriteInputFile(str(file), format_dict[format])

        # Bug in MPL with binary vars (added to INTEGERS block)
        if format == 'lp':
            lines = file.read_text().splitlines()
            processed_lines = []
            vector_bins = []
            for vector in self._mpl_model.VariableVectors: # vector.Type is often None (not set) and can't be used
                vector_bins.extend([var.Name for var in vector if var.IsBinary])
            plain_bins = [var.Name for var in self._mpl_model.PlainVariables if var.IsBinary]
            bin_vars = vector_bins + plain_bins
            if bin_vars:
                end_line_index = None
                for line in lines:
                    if 'END' == line.strip().upper():
                        end_line_index = len(processed_lines)
                    if not any([var_name == line.strip() for var_name in bin_vars]):
                        processed_lines.append(line)
                processed_lines.insert(end_line_index, 'BINARY')
                i = 0
                for i, var in enumerate(bin_vars, 1):
                    processed_lines.insert(end_line_index + i, var)
                processed_lines.insert(end_line_index + i + 1, '') # blank line after BINARY block
                file.write_text('\n'.join(processed_lines))

        return True

    def solve(self):

        if self._mpl_model:
            self._mpl_model.Solve()
            return self.obj_value
        else:
            raise RuntimeError(Messages.MSG_NO_MPL_MODEL_CANNOT_SOLVE)

    def _read_file(self, file: Path):

        if self._file is not None:
            raise RuntimeError(Messages.MSG_MODEL_READ_FILE_ONLY_ONCE)

        if not isinstance(file, Path):
            raise ValueError(Messages.MSG_FILE_SHOULD_BE_PATH)

        self._file = file

        if not self._file.is_file():
            raise FileNotFoundError(Messages.MSG_INSTANCE_FILE_NOT_FOUND)

        if not self.format in Model.supported_in_formats:
            raise RuntimeError(Messages.MSG_INPUT_FORMAT_NOT_SUPPORTED)

        try:
            if self.format in ['mpl', 'mps']: # these formats can be natively read with mpl.Model.ReadModel()
                self._mpl_model = mpl.Models.Add(str(self._file))
                old_cwd = Path(__file__).cwd()
                file_path = str(file.parent).replace('\\', '//')
                self._mpl_model.WorkingDirectory = file_path  # .dat file locations in .mpl file are defined relative to file location, ReadModel searches .dat files relative to cwd
                self._mpl_model.ReadModel(file.name)
                os.chdir(old_cwd)  # ReadModel() changes the cwd to model working directory, set it back
            elif self.format in ['lp']: # these formats are first tansformed to mpl as text and then read by mpl.Model with ParseModel()
                self._parse_file()
        except ModelResultException as e:
            raise RuntimeError(e)

    def _parse_file(self):

        if self.format == 'lp':
            mpl_string = self._parse_lp()
        else:
            raise NotImplementedError(Messages.MSG_MODEL_NO_PARSING_FOR_FORMAT)

        self._mpl_model = mpl.Models.Add(str(self._file))
        old_cwd = Path(__file__).cwd()
        self._mpl_model.ParseModel(mpl_string)
        os.chdir(old_cwd) # ParseModel() changes the cwd

    def _parse_lp(self):
        # This is cplex format
        # About CPLEX lp format: http://lpsolve.sourceforge.net/5.1/CPLEX-format.htm
        lp_string = self._file.read_text()
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

        return mpl_string

    def _mps2three(self, temp_file: Path, filename):
        lines_in_files = {'cor': [], 'tim': [], 'sto': []}
        text = temp_file.read_text()
        lines = text.split('\n')

        current_file_lines = 'cor'
        for line in lines:
            if current_file_lines == 'cor' and 'TIME' in line: # TIME block should go after COR
                current_file_lines = 'tim'
            elif current_file_lines == 'tim' and 'STOCH' in line:  # STOCH block should go after TIME
                current_file_lines = 'sto'
            elif 'EXPLICIT' in line and current_file_lines == 'sto':
                raise RuntimeError(Messages.MSG_EXPLICIT_IN_MPS)

            lines_in_files[current_file_lines].append(line)

        for extension in ['cor', 'tim', 'sto']:
            contents = lines_in_files[extension]
            if extension in ['cor', 'tim']:
                contents.append('ENDATA')

            file = Path(f'{filename}.{extension}')
            file.write_text('\n'.join(contents))

        # Delete the file
        temp_file.unlink()
