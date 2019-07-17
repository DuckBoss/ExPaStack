import sys
from .utils import FileAccessUtility, CliUtility, EncodingUtility, JSONUtility
from .exceptions import IncorrectInputError

class PrimaryRunner:
    object_path = ''
    def __init__(self):
        print("ExPaStack Initialized.")

        if len(sys.argv) > 1:
            self.object_path = CliUtility.get_cli_parameter(sys.argv)
        else:
            raise IncorrectInputError('One or more parameters have not been provided to the program.\n'
                                      'How to run: python3 <object_path> <optional_params>')

        self.parse_and_output(self.object_path)

    def parse_and_output(self, asset_path: str) -> None:
        file_content = FileAccessUtility.get_file_content(asset_path)
        # print(file_content)
        ext_type = FileAccessUtility.get_file_extension(asset_path)
        # print(ext_type.name)
        obj_names = FileAccessUtility.get_mesh_names(all_file_content=file_content, ext_type=ext_type)
        # print(obj_names)
        obj_ids = EncodingUtility.encode_strings(obj_names)
        # print(obj_ids)
        prepped_json = JSONUtility.prepare_for_json(obj_names, obj_ids)
        extra_check = JSONUtility.check_json(prepped_json)
        print(f'Error Checks Passed: {extra_check}')
        output_json = JSONUtility.pack_as_json(prepped_json, FileAccessUtility.get_file_name(asset_path))
        print(f'Successful JSON Output: {output_json}')
