from pathlib import Path
from optconvert import Model


class _DataItem():
    def __init__(self, model, name, data_type, filename_prefix):
        self._model = model
        self._name = name
        self._data_type = data_type
        self._filename_prefix = filename_prefix
        self._value = None

        file_contents = self.file.read_text()
        data = file_contents.split('\n')
        if data_type == 'scalar':
            row = data.index('!' + self._name) + 1
            self._value = data[row].strip()
        else: # vector_sparse or index_sparse
            # check the formatting
            first_line = data[0].strip()
            second_line = data[1].strip()
            if first_line[0] != '!' or second_line[0] != '!' or first_line[1:] != name:
                raise ValueError(
                    f'File {str(self.parse_filename())} formatted not correct: first two lines should be data name and indices as comments')

            keys = second_line[1:].split(',')
            value_data = data[2:]
            self._value = []
            # {index_1: ..., ...index_n: ..., value}
            for line in value_data:
                indices_and_value = line.split(',')
                record = dict(zip(keys, indices_and_value))  # {index_1: ..., ...index_n: ..., value}
                self._value.append(record)

    @property
    def file(self) -> Path:
        return self.parse_filename()

    def parse_filename(self, filename_prefix: str = None, out_folder: Path = None) -> Path:
        if filename_prefix is None:
            filename_prefix = self._filename_prefix
        if out_folder is None:
            out_folder = self._model._file.parent
        if self._data_type == 'scalar':
            return (out_folder / Path(filename_prefix + MplWithExtData.STR_SCALAR_DATA_TYPE_SUFFIX)).with_suffix('.dat')
        else:
            return (out_folder / Path(filename_prefix + self._name)).with_suffix('.dat')

    def set(self, new_value):
        # Will change the data file if necessary
        # The model should be reloaded after data is changed!
        self._value = new_value
        self.export()

    def export(self, filename_prefix: str = None, out_folder: Path = None) -> None:
        if filename_prefix is None:
            filename_prefix = self._filename_prefix
        if out_folder is None:
            out_folder = self._model._file.parent
        data = ''
        # load and modify the data from the current data file
        if self._data_type == 'scalar':
            with open(self.parse_filename(), 'r') as dat_file:
                data = dat_file.readlines()
                data_starts_from = data.index('!' + self._name + '\n')
                del data[data_starts_from + 1]  # delete the next row with data (we will write it now)
                data[data_starts_from] = str(self)
        elif self._data_type == 'vector_sparse' or self._data_type == 'index_sparse':  # but for sparse vector we write the whole new file
            data = str(self)

        # and write to the new file
        with open(self.parse_filename(filename_prefix, out_folder), 'w') as dat_file:
            dat_file.writelines(data)

    def __str__(self):
        if self._data_type == 'scalar':
            return str('!{}\n{}\n'.format(self._name, self._value))
        elif self._data_type == 'vector_sparse' or self._data_type == 'index_sparse':
            '''
            !
            1, 1\n
            '''
            keys = self._value[0].keys()
            first_two_lines = '!{}\n!{}\n'.format(self._name, ','.join(keys))
            data_lines = ''
            i = len(self._value)
            for record in self._value:
                next_line = ','.join([str(record[key]) for key in keys])
                if i > 1: # we are not on the last element
                    next_line += '\n'
                    i -= 1
                data_lines += next_line
            return first_two_lines + data_lines


class MplWithExtData(Model):
    """
    Extends the Model class.
    Used for .mpl models that have some or all of the data defined in the external .dat files.
    External data can be modified with set_ext_data() and saved as a new model instance.
    It allows the generation of multiple instances with the different data.

    Attributes
    ----------

    Methods
    -------
    set_ext_data(new_data_dict)
        changes the data in .dat files according to the new_data_dict

    Private Attributes
    -------
    _external_data : list
        list of _DataItem instances

    Private Methods
    -------
    _populate_ext_data
        fills _external_data attribute with _DataItem instances
    """

    STR_SCALAR_DATA_TYPE_SUFFIX = 'ScalarData' # file_STR_SCALAR_DATA_TYPE_SUFFIX.dat

    def __init__(self, file: Path):
        super().__init__(file)
        if self.format != 'mpl':
            raise RuntimeError('mpl model with external data should be read from .mpl file')
        self._external_data = self._populate_ext_data()

    def _populate_ext_data(self):
        data_list = {}
        data_type = 'scalar'
        dat_file_prefix = self._file.stem + '_'
        # we assume that .dat files or in the same folder as the .mpl file
        dat_file_path = Path(self._mpl_model.WorkingDirectory) / f'{dat_file_prefix}{MplWithExtData.STR_SCALAR_DATA_TYPE_SUFFIX}.dat'
        data_items_in_file = []
        if dat_file_path.is_file(): # if data file exists
            with open(str(dat_file_path), 'r') as dat_file:
                # !Demand -> Demand
                data_items_in_file = [line.strip()[1:] for line in dat_file if line.startswith('!')]

        for constant in self._mpl_model.DataConstants:
            # check whether data is taken from the data file edited according to requirement.
            name = constant.Name
            if name not in data_items_in_file:
                continue
            data_item = _DataItem(self, name, data_type, self._file.stem + '_')
            data_list[name] = data_item

        for string in self._mpl_model.DataStrings:
            raise NotImplementedError(False and 'not implemented work with strings data')

        data_type = 'vector_sparse'
        for vector in self._mpl_model.DataVectors:
            name = vector.Name
            # every vector is stored in the separate file
            dat_file_path = self._file.parent / Path(f'{self._file.stem}_{name}.dat')
            # check whether data is taken from the data file
            if not dat_file_path.is_file():
                continue
            vector_type = vector.Type # 0 - unknown, 1 - dense, 2 - sparse, 3 - random, 4 - prob
            if vector_type == 1:
                raise NotImplementedError(f'Vector data in datafiles should be stored in sparse form. It is not like that for: {str(dat_file_path)}')
            data_item = _DataItem(self, name, data_type, dat_file_prefix)
            data_list[name] = data_item

        data_type = 'index_sparse'
        for index_set in self._mpl_model.IndexSets:
            name = index_set.Name
            # every vector is stored in the separate file
            dat_file_path = self._file.parent / Path(f'{self._file.stem}_{name}.dat')
            # check whether data is taken from the data file edited according to requirements
            if not dat_file_path.is_file():
                continue
            data_item = _DataItem(self, name, data_type, dat_file_prefix)
            data_list[name] = data_item

        return data_list

    def set_ext_data(self, new_data_dict):
        """Updates the data in the .dat files (if any) and reparses the model to include this data.

        Parameters
        ----------
        new_data_dict : dict
            {data_item_name: new_value}

        Returns
        -------
        None
        """

        for data_item_name, new_value in new_data_dict.items():
            data_item = self._external_data.get(data_item_name)
            if data_item is None:
                raise ValueError(f'{data_item_name} is unknown data item. Check the name provided.')
            data_item.set(new_value)
        # we need to reload the model with updated data file
        old_file = self._file
        self._file = None # we can read the file only once. Do this to overcome the issue
        self._read_file(old_file)

    def export(self, file: Path = None):
        if file == None:
            format = self.format
            name = self._file.stem
        else:
            format = file.suffix[1:]
            name = file.stem

        if format == 'mpl':
            model_formulation = self._file.read_text()
            # update links in the model formulation
            model_formulation = model_formulation.replace(self._file.stem, name)
            file.write_text(model_formulation)
            # export .dat files
            for data_item in self._external_data.values():
                dat_filename_prefix = name+'_'
                data_item.export(dat_filename_prefix, file.parent)
        else:
            super().export(file)
