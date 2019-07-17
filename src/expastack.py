import sys
from .utils import FileAccessUtility, CliUtility, EncodingUtility, JSONUtility
from .exceptions import IncorrectInputError
import assets.config as config

class PrimaryRunner:
    object_path = ''
    optional_params = []

    filter_list = []
    filter_type = ''
    def __init__(self):
        print('ExPaStack Initialized.')

        if len(sys.argv) > 1:
            print(f'Processing file: {FileAccessUtility.get_file_name(sys.argv[1])}.{FileAccessUtility.get_file_extension(sys.argv[1]).name.lower()}')
            self.object_path = CliUtility.get_cli_parameter(sys.argv)
            self.optional_params = CliUtility.get_optional_parameters(sys.argv)
            self.process_optional_params(self.optional_params)
        else:
            raise IncorrectInputError('One or more parameters have not been provided to the program.\n'
                                      'How to run: python3 <object_path> <optional_params>')
        if self.filter_type == '':
            self.filter_type = config.filter_type
        if not self.filter_list:
            self.filter_list = config.filter_list

        self.parse_and_output(self.object_path)

    def process_optional_params(self, optional_params):
        for i, tup in enumerate(optional_params):
            print(tup)
            if tup[0] == 'keywords':
                self.filter_list = tup[1].replace(' ', '').split(',')
                print(f'Filter List: {self.filter_list}')
            elif tup[0] == 'filter-type':
                self.filter_type = tup[1].replace(' ', '').strip()
                if not (self.filter_type == 'include' or self.filter_type == 'exclude'):
                    raise RuntimeError('The filter type must can only be "include" or "exclude"')
                print(f'Filter Type: {self.filter_type}')

    def parse_and_output(self, asset_path: str) -> None:
        file_content = FileAccessUtility.get_file_content(asset_path)
        # print(file_content)
        ext_type = FileAccessUtility.get_file_extension(asset_path)
        # print(ext_type.name)
        obj_names = FileAccessUtility.get_mesh_names(all_file_content=file_content, ext_type=ext_type)
        # print(obj_names)
        obj_ids = EncodingUtility.encode_strings(obj_names)
        # print(obj_ids)
        prepped_json = JSONUtility.prepare_for_json(obj_names, obj_ids, self.filter_list, self.filter_type)
        extra_check = JSONUtility.check_json(prepped_json)
        print(f'Error Checks Passed: {extra_check}')
        output_json = JSONUtility.pack_as_json(prepped_json, FileAccessUtility.get_file_name(asset_path))
        print(f'Successful JSON Output: {output_json}')
