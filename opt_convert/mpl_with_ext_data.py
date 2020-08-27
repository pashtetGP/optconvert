from pathlib import Path
from opt_convert import Model


class _DataItem():
    def __init__(self, name, data_type, filename_prefix):
        self._name_ = name
        self._data_type_ = data_type
        self._filename_prefix_ = filename_prefix
        self._value_ = None

        dat_file = open(self.get_filename() + '.dat', mode='r')
        data = dat_file.readlines()
        dat_file.close()
        if data_type == 'scalar':
            row = data.index('!' + self._name_ + '\n') + 1
            self._value_ = data[row].strip()
        else: # vector_sparse or index_sparse
            # check the formatting
            first_line = data[0].strip()
            second_line = data[1].strip()
            if first_line[0] != '!' or second_line[0] != '!' or first_line[1:] != name:
                raise ValueError(
                    f'File {str(self.get_filename())}.dat formatted not correct: first two lines should be data name and indices as comments')

            keys = second_line[1:].split(',')
            value_data = data[2:]
            self._value_ = []
            # {index_1: ..., ...index_n: ..., value}
            for line in value_data:
                line = line.replace('\n', '')
                indices_and_value = line.split(',')
                record = dict(zip(keys, indices_and_value))  # {index_1: ..., ...index_n: ..., value}
                self._value_.append(record)

    def get_filename(self):
        if self._data_type_ == 'scalar':
            return self._filename_prefix_ + MplWithExtData.STR_SCALAR_DATA_TYPE_SUFFIX
        else:
            return self._filename_prefix_ + self._name_

    def set(self, new_value, file = None, quiet = False):
        # Will change the data file if necessary
        # The model should be reloaded after data is changed!
        self._value_ = new_value
        self.export()

    def export(self, filename_prefix=None):
        if filename_prefix is None:
            filename_prefix = self._filename_prefix_
        data = ''
        # load and modify the data from the current data file
        if self._data_type_ == 'scalar':
            with open(self.get_filename() + '.dat', 'r') as dat_file:
                data = dat_file.readlines()
                data_starts_from = data.index('!' + self._name_ + '\n')
                del data[data_starts_from + 1]  # delete the next row with data (we will write it now)
                data[data_starts_from] = str(self)
        elif self._data_type_ == 'vector_sparse' or self._data_type_ == 'index_sparse':  # but for sparse vector we write the whole new file
            data = str(self)

        # and write to the new file
        output_filename = ''
        if self._data_type_ == 'scalar':
            output_filename = filename_prefix + MplWithExtData.STR_SCALAR_DATA_TYPE_SUFFIX
        else:
            output_filename = filename_prefix + self._name_
        with open(output_filename+'.dat', 'w') as dat_file:
            dat_file.writelines(data)

    def __str__(self):
        if self._data_type_ == 'scalar':
            return str('!{}\n{}\n'.format(self._name_, self._value_))
        elif self._data_type_ == 'vector_sparse' or self._data_type_ == 'index_sparse':
            '''
            !
            1, 1\n
            '''
            keys = self._value_[0].keys()
            first_two_lines = '!{}\n!{}\n'.format(self._name_, ','.join(keys))
            data_lines = ''
            i = len(self._value_)
            for record in self._value_:
                next_line = ','.join([str(record[key]) for key in keys])
                if i > 1: # we are not on the last element
                    next_line += '\n'
                    i -= 1
                data_lines += next_line
            return first_two_lines + data_lines


class MplWithExtData(Model):

    STR_SCALAR_DATA_TYPE_SUFFIX = 'ScalarData' # file_STR_SCALAR_DATA_TYPE_SUFFIX.dat

    def __init__(self, file: Path):
        super().__init__(file)
        if self.format != 'mpl':
            raise RuntimeError('mpl model with external data should be read from .mpl file')
        self._external_data_ = self._populate_ext_data()

    def _populate_ext_data(self):
        data_list = {}
        data_type = 'scalar'
        dat_file_prefix = self.file.stem + '_'
        dat_file_path = Path(f'{dat_file_prefix}{MplWithExtData.STR_SCALAR_DATA_TYPE_SUFFIX}.dat')
        data_items_in_file = []
        if dat_file_path.is_file(): # if data file exists
            with open(str(dat_file_path), mode='r') as dat_file:
                # !Demand -> Demand
                data_items_in_file = [line.strip()[1:] for line in dat_file if line.startswith('!')]

        for constant in self.mpl_model.DataConstants:
            # check whether data is taken from the data file edited according to requirement.
            name = constant.Name
            if name not in data_items_in_file:
                continue
            data_item = _DataItem(name, data_type, self.file.stem + '_')
            data_list[name] = data_item

        for string in self.mpl_model.DataStrings:
            raise NotImplementedError(False and 'not implemented work with strings data')

        data_type = 'vector_sparse'
        for vector in self.mpl_model.DataVectors:
            name = vector.Name
            # every vector is stored in the separate file
            dat_file_path = Path(f'{self.file.stem}_{name}.dat')
            # check whether data is taken from the data file
            if not dat_file_path.is_file():
                continue
            vector_type = vector.Type # 0 - unknown, 1 - dense, 2 - sparse, 3 - random, 4 - prob
            if vector_type == 1:
                raise NotImplementedError(f'Vector data in datafiles should be stored in sparse form. It is not like that for: {str(dat_file_path)}')
            data_item = _DataItem(name, data_type, dat_file_prefix)
            data_list[name] = data_item

        data_type = 'index_sparse'
        for index_set in self.mpl_model.IndexSets:
            name = index_set.Name
            # every vector is stored in the separate file
            dat_file_path = Path(f'{self.file.stem}_{name}.dat')
            # check whether data is taken from the data file edited according to requirements
            if not dat_file_path.is_file():
                continue
            data_item = _DataItem(name, data_type, dat_file_prefix)
            data_list[name] = data_item

        return data_list

    def set_ext_data(self, new_data_dict):
        '''
        Update the data in the .dat file (if any) and reparse the model to include this data.
        :param new_data_dict: {data_item_name: new_value}
        :return: nothing
        '''

        for data_item_name, new_value in new_data_dict.items():
            data_item = self._external_data_.get(data_item_name)
            if data_item is None:
                raise ValueError(f'{data_item_name} is unknown data item. Check the name provided.')
            data_item.set(new_value)
        # we need to reload the model with updated data file
        old_file = self.file
        self.file = None # we can read the file only once. Do this to overcome the issue
        self._read_file(old_file)

    def export(self, format=None, name=None):
        if format is None:
            format = self.format
        if name is None:
            name = self.file.stem
        if format == 'mpl':
            with open(str(self.file), 'r') as original_file:
                model_formulation = original_file.read()
                # update links in the model formulation
                model_formulation = model_formulation.replace(self.file.stem, name)
                new_file = open(name + '.mpl', 'w')
                new_file.write(model_formulation)
                new_file.close()
            # export .dat files
            for data_item in self._external_data_.values():
                dat_filename_prefix = name+'_'
                data_item.export(dat_filename_prefix)
        else:
            super().export(format, name)
