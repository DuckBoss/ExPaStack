from math import ceil
from typing import List, Dict, Union, Tuple
from .exceptions import JSONPackingError, DuplicateObjectNameError, FileNotSupportedError
import json
import xml.etree.ElementTree as ElementTree
import hashlib
from enum import Enum


class CompatibilityUtility:
    class CompatibleFileExtension(Enum):
        OBJ = 0,
        GLTF = 1,
        DAE = 2

class CliUtility:
    @staticmethod
    def get_optional_parameters(args: List[str]) -> List[Tuple[str, str]]:
        if len(args) > 1:
            ret_list = []
            for i, arg in enumerate(args[1:]):
                if arg[:2] == '--':
                    try:
                        ret_list.append((arg[2:], args[i+2]))
                    except IndexError:
                        raise IndexError("The optional parameter must include a value!")
            return ret_list
        return [('','')]

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
    def get_file_extension(file_path: str) -> CompatibilityUtility.CompatibleFileExtension:
        try:
            return CompatibilityUtility.CompatibleFileExtension[f"{file_path.split('/')[-1][::-1].split('.')[0][::-1].upper()}"]
        except KeyError:
            raise FileNotSupportedError(f"The file type: {file_path.split('/')[-1][::-1].split('.')[0][::-1].upper()} is currently not supported.")

    @staticmethod
    def get_file_name(file_path: str) -> str:
        return file_path.split('/')[-1][::-1].split('.')[1][::-1]

    @staticmethod
    def get_raw_file_name(file_path: str) -> str:
        return file_path[::-1].split('.')[1][::-1]

    @staticmethod
    def get_file_content(file_name: str, ext_type: CompatibilityUtility.CompatibleFileExtension = None) -> Union[List[str], Dict[str, str], ElementTree.Element]:
        full_file_name = f'{file_name}'
        if ext_type is None:
            ext_type = FileAccessUtility.get_file_extension(file_name)
            file_name = FileAccessUtility.get_raw_file_name(file_name)
            if not any(x for x in CompatibilityUtility.CompatibleFileExtension if x == ext_type):
                raise FileNotSupportedError(f'The file type: {ext_type.name} is currently not supported.')
            full_file_name = f'{file_name}.{ext_type.name}'
        try:
            if ext_type == CompatibilityUtility.CompatibleFileExtension.OBJ:
                with open(f'{full_file_name}', 'r') as obj_file:
                    all_lines = obj_file.readlines()
            elif ext_type == CompatibilityUtility.CompatibleFileExtension.GLTF:
                with open(f'{full_file_name}') as json_file:
                    all_lines = json.load(json_file)
            elif ext_type == CompatibilityUtility.CompatibleFileExtension.DAE:
                root = ElementTree.parse(full_file_name).getroot()
                return root
            else:
                all_lines = []
        except FileNotFoundError:
            raise FileNotFoundError('The file could not be found!')
        except IsADirectoryError:
            raise FileNotFoundError('The given path is a directory, not a file!')
        return all_lines

    @staticmethod
    def get_mesh_names(all_file_content: Union[Dict[str, str], List[str], ElementTree.Element] = None, ext_type: CompatibilityUtility.CompatibleFileExtension = CompatibilityUtility.CompatibleFileExtension.OBJ) -> List[str]:
        all_obj_names = []

        if ext_type == CompatibilityUtility.CompatibleFileExtension.OBJ:
            for i, line in enumerate(all_file_content):
                if line[0] == 'o':
                    new_mesh_name = line[2:].strip('\n')
                    if new_mesh_name in all_obj_names:
                        raise DuplicateObjectNameError('This mesh name exists multiple times in the obj file. Each mesh must be uniquely named!')
                    all_obj_names.append(line[2:].strip('\n'))
            return all_obj_names
        elif ext_type == CompatibilityUtility.CompatibleFileExtension.GLTF:
            json_content = all_file_content['meshes']
            for item in json_content:
                all_obj_names.append(item['name'])
            return all_obj_names
        elif ext_type == CompatibilityUtility.CompatibleFileExtension.DAE:
            for items in all_file_content:
                for item in items:
                    if 'geometry' in item.tag:
                        all_obj_names.append(item.attrib['name'])
        return all_obj_names

class JSONUtility:
    @staticmethod
    def prepare_for_json(obj_names: List[str], obj_ids: List[int], filter_list: List[str], filter_type: str = 'include', map_names: dict = None, include_header = False) -> Dict[str, str]:
        if len(obj_names) != len(obj_ids):
            from .exceptions import DataMismatchError
            raise DataMismatchError('The length of the mesh names and the encoded mesh ids are not the same.\n'
                                    'This usually means that the data sets do not belong to each other.\n'
                                    'Please make sure the correct data sets are passed into the method.')
        json_struct = {}
        for i, val in enumerate(obj_names):
            try:
                parsed_name = obj_names[i][::-1].split('_', 1)[1][::-1]
            except IndexError:
                parsed_name = val
            if len(filter_list) > 0:
                if parsed_name in filter_list:
                    if filter_type == 'exclude':
                        continue
                    else:
                        if include_header:
                            json_struct[f'{parsed_name}'] = {
                                'mesh': parsed_name,
                                'name': map_names[parsed_name] if parsed_name in map_names else parsed_name,
                                'uid': (hashlib.md5(str(obj_ids[i]).encode())).hexdigest()
                            }
                        else:
                            json_struct[f'mesh_{i}'] = {
                                'mesh': parsed_name,
                                'name': map_names[parsed_name] if parsed_name in map_names else parsed_name,
                                'uid': (hashlib.md5(str(obj_ids[i]).encode())).hexdigest()
                            }
                else:
                    if filter_type == 'exclude':
                        if include_header:
                            json_struct[f'{parsed_name}'] = {
                                'mesh': parsed_name,
                                'name': map_names[parsed_name] if parsed_name in map_names else parsed_name,
                                'uid': (hashlib.md5(str(obj_ids[i]).encode())).hexdigest()
                            }
                        else:
                            json_struct[f'mesh_{i}'] = {
                                'mesh': parsed_name,
                                'name': map_names[parsed_name] if parsed_name in map_names else parsed_name,
                                'uid': (hashlib.md5(str(obj_ids[i]).encode())).hexdigest()
                            }

            else:
                if include_header:
                    json_struct[f'{parsed_name}'] = {
                        'mesh': parsed_name,
                        'name': map_names[parsed_name] if parsed_name in map_names else parsed_name,
                        'uid': (hashlib.md5(str(obj_ids[i]).encode())).hexdigest()
                    }
                else:
                    json_struct[f'mesh_{i}'] = {
                        'mesh': parsed_name,
                        'name': map_names[parsed_name] if parsed_name in map_names else parsed_name,
                        'uid': (hashlib.md5(str(obj_ids[i]).encode())).hexdigest()
                    }
        return json_struct

    @staticmethod
    def check_json(prepared_json_content: Dict[str, str]) -> bool:
        hash_list = []
        if len(prepared_json_content.items()) == 0:
            print("Warning: The resulting json output file is empty. If this isn't the intended behaviour, please check your keyword filters.")
        for i, val in prepared_json_content.items():
            if val['uid'] in hash_list:
                return False
            hash_list.append(val['uid'])
        return True

    @staticmethod
    def pack_as_json(json_prepared_data, file_name):
        try:
            with open(f'{file_name}.json', 'w') as outfile:
                json.dump(json_prepared_data, outfile)
                return True
        except Exception:
            raise JSONPackingError('There was a problem saving the JSON data to a file.')