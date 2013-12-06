import copy
import os
from doit.tools import create_folder

import file_utils

#------------------------------------------------------------------------
# constants

DEFAULT_ENV = {
    'c compiler': 'gcc',
    'c++ compiler': 'gcc',
    'linker': 'gcc',

    'c preprocessor defs': [],
    'c++ preprocessor defs': [],

    'c compiler flags': ['-c', '-MMD'],
    'c++ compiler flags': ['-c', '-MMD'],

    'c header search paths': [],
    'c++ header search paths': [],

    'linker script': None,
    'linker libraries': [],
    'linker flags': [],
    'linker library search paths': [],
}


#------------------------------------------------------------------------
# data

local_env = copy.deepcopy(DEFAULT_ENV)


#------------------------------------------------------------------------
# public functions

def get_env():
    return local_env


def set_env(env):
    global local_env
    local_env = env


def update_env(env):
    local_env.update(env)


def get_obj_target_paths(sources, build_dir):
    """ Return the object file destination paths
        for the given source files """
    return [_source_to_obj_path(x, build_dir) for x in sources]


def get_dep_target_paths(sources, build_dir):
    """ Return the dependency file destination paths
        for the given source files """
    return [_source_to_dep_path(x, build_dir) for x in sources]


def get_c_compile_tasks(sources, build_dir):
    """ Return a list of doit tasks for compiling the given c source files """
    tasks = []
    depmap = get_dependency_dict(build_dir)
    for source in sources:
        obj = _source_to_obj_path(source, build_dir)
        dep = _source_to_dep_path(source, build_dir)
        source_deps = depmap.get(source, [source])
        tasks.append({
            'name': obj,
            'actions': [(create_folder, [os.path.dirname(obj)]),
                        get_compile_cmd_str(source, obj,
                                            compiler=local_env['c compiler'],
                                            defs=local_env['c preprocessor defs'],
                                            includes=local_env['c header search paths'],
                                            flags=local_env['c compiler flags'])],
            'targets': [obj, dep],
            'file_dep': source_deps,
            'clean': True
        })
    return tasks


def get_cpp_compile_tasks(sources, build_dir):
    """ Return a list of doit tasks for compiling the given c++ source files """
    tasks = []
    depmap = get_dependency_dict(build_dir)
    for source in sources:
        obj = _source_to_obj_path(source, build_dir)
        dep = _source_to_dep_path(source, build_dir)
        source_deps = depmap.get(source, [source])
        tasks.append({
            'name': obj,
            'actions': [(create_folder, [os.path.dirname(obj)]),
                        get_compile_cmd_str(source, obj,
                                            compiler=local_env['c++ compiler'],
                                            defs=local_env['c++ preprocessor defs'],
                                            includes=local_env['c++ header search paths'],
                                            flags=local_env['c++ compiler flags'])],
            'targets': [obj, dep],
            'file_dep': source_deps,
            'clean': True
        })
    return tasks


def get_link_exe_tasks(objs, target):
    return [{
        'name': target,
        'actions': [get_link_cmd_str(target, objs,
                                     linker=local_env['linker'],
                                     libdirs=local_env['linker library search paths'],
                                     libs=local_env['linker libraries'],
                                     flags=local_env['linker flags'])],
        'file_dep': objs,
        'targets': [target],
        'clean': True
    }]


def get_compile_cmd_str(src, obj, compiler='gcc', defs=[], includes=[], flags=[]):
    cmd_args = [compiler]
    cmd_args += ['-D'+d for d in defs]
    cmd_args += ['-I'+i for i in includes]
    cmd_args += flags
    if '-c' not in flags:
        cmd_args += ['-c']
    cmd_args += ['-o', obj]
    cmd_args += [src]
    return _arg_list_to_command_string(cmd_args)


def get_link_cmd_str(target, objs, linker='gcc', libdirs=[], libs=[], flags=[],
                     linker_script=None):
    cmd_args = [linker]
    cmd_args += flags
    cmd_args += ['-L'+d for d in libdirs]
    if linker_script is not None:
        cmd_args += ['-T'+linker_script]
    cmd_args += ['-o', target]
    cmd_args += objs
    cmd_args += ['-l'+lib for lib in libs]
    return _arg_list_to_command_string(cmd_args)


def get_dependency_dict(path, depfile_pattern='*.d'):
    """ Search path and all subdirectories for dependency files,
        return a dictionary of target : [dependencies] pairs
    """
    depfiles = file_utils.find(path, depfile_pattern, search_subdirs=True)
    deps = {}
    for dep in depfiles:
        deps.update(read_dependency_file(dep))
    return deps


def read_dependency_file(path):
    """ Scan a gcc-generated dependency file for targets
        and their dependencies. Returns a dictionary of
        target : [dependencies] pairs
    """

    def get_target_from_line(line):
        """ Return target, remainder if a target found in the line.
            Otherwise return None, None
        """
        line_split = line.split(': ')
        if len(line_split) == 2:
            return line_split[0], line_split[1]
        return None, None

    def get_deps_from_string(string):
        return [s for s in string.split() if s != '\\']

    target_dict = {}
    with open(path) as infile:
        current_target = None
        current_deps = []
        for line in infile:
            tgt, remainder = get_target_from_line(line)
            if tgt is None:
                current_deps += get_deps_from_string(line)
            else:
                if current_target is not None:
                    target_dict[current_target] = current_deps
                current_target = tgt
                current_deps = get_deps_from_string(remainder)
    target_dict[current_target] = current_deps
    return target_dict


#------------------------------------------------------------------------
# private functions

def _source_to_obj_path(src, build_dir):
    src_filename = os.path.basename(src)
    return os.path.join(build_dir, 'obj', src_filename) + '.o'


def _source_to_dep_path(src, build_dir):
    src_filename = os.path.basename(src)
    return os.path.join(build_dir, 'obj', src_filename) + '.d'


def _arg_list_to_command_string(arg_list):
    return ' '.join([str(arg) for arg in arg_list])
