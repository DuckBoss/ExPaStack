# ExPaStack [EPS]
Extract, Pack, and Stack! Extract 3d obj/gltf/dae mesh names into a JSON format with unique ids.

[![GitHub](https://img.shields.io/github/license/DuckBoss/ExPaStack.svg?style=for-the-badge)](https://github.com/DuckBoss/ExPaStack/releases)
[![GitHub release](https://img.shields.io/github/release/DuckBoss/ExPaStack.svg?style=for-the-badge)](https://github.com/DuckBoss/ExPaStack/blob/master/LICENSE)

## Usage
Basic Usage:
```
python3 expastack assets/cube.obj
```
Command-line parameters usage:
```
python3 expastack assets/cube.gltf --keywords "Cube1, Cube2" --filter-type "exclude"
```


## Command Line Parameters
```
--keywords "..."
--filter-type "include/exclude"
```
#### Keywords Parameter
```
--keywords "mesh_1, mesh_2" : Mesh names to filter in the output json
```

#### Filter Type Parameter
```
--filter-type "include/exclude" : Either filters out the keyword mesh names from the json output(exclude)
                                  or it only includes the keyword mesh names in the json output. 
```


## Configuration Python File
If you have many keywords to filter, then consider using the config.py file provided
in the root directory.<br>
This will help avoid long command line parameters.


## Example Output
Generates a json file in the root directory.
```
Input: python3 expastack cube.obj
Output: cube.json
{
    "Cube"
    {
        "name" = "Cube",
        "uid" = "aisodjiasd092941298401928jf"
    }
}
```
```
Input: python3 expastack complex_object.obj --filter-type "include" --keywords "mesh1, mesh2"
Output: complex_object.json
{
    "mesh1" { "name"= "mesh1", "uid" = <generated_uid> }
    "mesh2" { "name"= "mesh2", "uid" = <generated_uid> }
    (includes only mesh names in the filtered keywords)
}
```
```
Input: python3 expastack complex_object.obj --filter-type "exclude" --keywords "mesh1, mesh2"
Output: complex_object.json
{
    ... { "name" = <mesh_name>, "uid" = <generated_uid> }
    ...
    ...
    ... (includes all mesh names except filtered keywords)
}
```
