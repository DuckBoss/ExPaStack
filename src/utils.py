from math import ceil
from typing import List, Dict
from .exceptions import JSONPackingError, DuplicateObjectNameError, FileNotSupportedError
import json
import hashlib


class CompatibilityUtility:
    compatible_file_types = ['obj']

class CliUtility:
    @staticmethod
    def get_cli_parameter(args: List[str]) -> str:
        if len(args) > 1:
            for i, arg in enumerate(args[1:]):
                if arg[:2] != '--':
                    return arg
        return ''

class EncodingUtility:
    @staticmethod
    def encode_string(obj_name: str) -> int:
        return int.from_bytes(obj_name.encode(), 'little')

    @staticmethod
    def encode_strings(obj_names: List[str]) -> List[int]:
        all_encoded_objs = []
        for i, obj in enumerate(obj_names):
            all_encoded_objs.append(int.from_bytes(obj.encode(), 'little'))
        return all_encoded_objs

    @staticmethod
    def decode_string(obj_id: int) -> str:
        return obj_id.to_bytes(int(ceil(obj_id.bit_length() / 8)), 'little').decode()

    @staticmethod
    def decode_strings(obj_ids: List[int]) -> List[str]:
        all_decoded_objs = []
        for i, obj in enumerate(obj_ids):
            all_decoded_objs.append(obj.to_bytes(int(ceil(obj.bit_length() / 8)), 'little').decode())
        return all_decoded_objs

class FileAccessUtility:
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        return file_path.split('/')[-1][::-1].split('.')[0][::-1]

    @staticmethod
    def get_file_name(file_path: str) -> str:
        return file_path.split('/')[-1][::-1].split('.')[1][::-1]

    @staticmethod
    def get_raw_file_name(file_path: str) -> str:
        return file_path[::-1].split('.')[1][::-1]

    @staticmethod
    def get_file_content(file_name: str, ext_type: str = None) -> List[str]:
        full_file_name = f'{file_name}'
        if ext_type is None:
            ext_type = FileAccessUtility.get_file_extension(file_name)
            file_name = FileAccessUtility.get_raw_file_name(file_name)
            if ext_type not in CompatibilityUtility.compatible_file_types:
                raise FileNotSupportedError(f'The file type: {ext_type} is currently not supported.')
            full_file_name = f'{file_name}.{ext_type}'
        try:
            with open(f'{full_file_name}', 'r') as obj_file:
                all_lines = obj_file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError('The file could not be found!')
        except IsADirectoryError:
            raise FileNotFoundError('The given path is a directory, not a file!')
        return all_lines

    @staticmethod
    def get_mesh_names(all_file_content: str = None, all_file_content_list: List[str] = None, ext_type: str = 'obj') -> List[str]:
        if all_file_content is None and all_file_content_list is None:
            raise RuntimeError('File content must be passed in either a string or a string list format!')
        if all_file_content and all_file_content_list:
            raise RuntimeError('Only a string file content OR a list of string file content is allowed!')
        all_obj_names = []


        if all_file_content:
            all_file_content_list = all_file_content.split('\n')
        if ext_type == 'obj':
            for i, line in enumerate(all_file_content_list):
                if line[0] == 'o':
                    new_mesh_name = line[2:].strip('\n')
                    if new_mesh_name in all_obj_names:
                        raise DuplicateObjectNameError('This mesh name exists multiple times in the obj file. Each mesh must be uniquely named!')
                    all_obj_names.append(line[2:].strip('\n'))
            return all_obj_names
        return []

class JSONUtility:
    @staticmethod
    def prepare_for_json(obj_names: List[str], obj_ids: List[int]) -> Dict[str, str]:
        if len(obj_names) != len(obj_ids):
            from .exceptions import DataMismatchError
            raise DataMismatchError('The length of the mesh names and the encoded mesh ids are not the same.\n'
                                    'This usually means that the data sets do not belong to each other.\n'
                                    'Please make sure the correct data sets are passed into the method.')
        json_struct = {}
        for i, val in enumerate(obj_names):
            json_struct[f'mesh_{i}'] = {
                'name': obj_names[i],
                'uid': (hashlib.md5(str(obj_ids[i]).encode())).hexdigest()
            }
        return json_struct

    @staticmethod
    def check_json(prepared_json_content: Dict[str, str]) -> bool:
        hash_list = []
        for i, val in prepared_json_content.items():
            if val['uid'] in hash_list:
                return False
            hash_list.append(val['uid'])
        return True

    @staticmethod
    def pack_as_json(json_prepared_data):
        try:
            with open('data.json', 'w') as outfile:
                json.dump(json_prepared_data, outfile)
                return True
        except Exception:
            raise JSONPackingError('There was a problem saving the JSON data to a file.')