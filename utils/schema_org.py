import enum
import os

INDENT_SPACES = 4


def make_schema_org_hierarchy_and_enum(enum_name, schema_file_name):
    parents = []
    types = {}
    type_tree = {}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path+'/../models/'+schema_file_name+'.schema') as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            last_space_pos = line.rstrip().rfind(' ')
            if last_space_pos:
                level = int((last_space_pos + 1) / INDENT_SPACES)
            else:
                level = 0
            parents = parents[0:level]
            new_type = line.strip()
            type_tree[new_type] = parents+[new_type]
            types[new_type] = new_type
    new_enum = enum.Enum(enum_name, types)
    hierarchy = {}
    for t, parents in type_tree.items():
        hierarchy[t] = list(map(lambda pt: new_enum(pt).value, parents))
    return (hierarchy, new_enum)
