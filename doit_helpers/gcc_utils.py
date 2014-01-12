import copy
import os
from doit.tools import create_folder

import file_utils

#------------------------------------------------------------------------
# constants

DEFAULT_ENV = {
    'c compiler': 'gcc',
    'c preprocessor defs': [],
    'c compiler flags': ['-c', '-MMD'],
    'c header search paths': [],
    'c source files': [],

    'c++ compiler': 'gcc',
    'c++ preprocessor defs': [],
    'c++ compiler flags': ['-c', '-MMD'],
    'c++ header search paths': [],
    'c++ source files': [],

    'linker': 'gcc',
    'linker script': None,
    'linker libraries': [],
    'linker flags': [],
    'linker library search paths': [],
}

#------------------------------------------------------------------------


class GccEnv:

    """ gcc environment class. Stores environment variables such
        as compiler path, preprocessor definitions etc., and provides
        methods for generating doit tasks to compile and link programs.
    """

    #------------------------------------------------
    # public

    def __init__(self, build_dir):
        self.variables = copy.deepcopy(DEFAULT_ENV)
        self.variables['build directory'] = build_dir

    def get_c_compile_tasks(self):
        """ Return a list of doit tasks for compiling the c source files
            set in the environment variables.
        """
        tasks = []
        depmap = get_dependency_dict(self.variables['build directory'])
        for source in self.variables['c source files']:
            obj = self._source_to_obj_path(
                source, self.variables['build directory'])
            dep = self._source_to_dep_path(
                source, self.variables['build directory'])
            source_deps = depmap.get(source, [source])
            tasks.append({
                'name': obj,
                'actions': [(create_folder, [os.path.dirname(obj)]),
                            get_compile_cmd_str(source, obj,
                                                compiler=self.variables[
                                                    'c compiler'],
                                                defs=self.variables[
                                                    'c preprocessor defs'],
                                                includes=self.variables[
                                                    'c header search paths'],
                                                flags=self.variables[
                                                    'c compiler flags'])],
                'targets': [obj, dep],
                'file_dep': source_deps,
                'clean': True
            })
        return tasks

    def get_cpp_compile_tasks(self):
        """ Return a list of doit tasks for compiling the c++ source files
            set in the environment variables.
        """
        tasks = []
        depmap = get_dependency_dict(self.variables['build directory'])
        for source in self.variables['c++ source files']:
            obj = self._source_to_obj_path(
                source, self.variables['build directory'])
            dep = self._source_to_dep_path(
                source, self.variables['build directory'])
            source_deps = depmap.get(source, [source])
            tasks.append({
                'name': obj,
                'actions': [(create_folder, [os.path.dirname(obj)]),
                            get_compile_cmd_str(source, obj,
                                                compiler=self.variables[
                                                    'c++ compiler'],
                                                defs=self.variables[
                                                    'c++ preprocessor defs'],
                                                includes=self.variables[
                                                    'c++ header search paths'],
                                                flags=self.variables[
                                                    'c++ compiler flags'])],
                'targets': [obj, dep],
                'file_dep': source_deps,
                'clean': True
            })
        return tasks

    def get_link_exe_tasks(self, exe_output):
        return [{
            'name': exe_output,
            'actions': [get_link_cmd_str(exe_output, self.get_all_objs(),
                                         linker=self.variables['linker'],
                                         libdirs=self.variables[
                                             'linker library search paths'],
                                         libs=self.variables[
                                             'linker libraries'],
                                         flags=self.variables[
                                             'linker flags'])],
            'file_dep': self.get_all_objs(),
            'targets': [exe_output],
            'clean': True
        }]

    def get_all_objs(self):
        """ Return a list of all compiler output objects (.o files) """
        all_sources = self.variables[
            'c source files'] + self.variables['c++ source files']
        objs = []
        for src in all_sources:
            objs.append(self._source_to_obj_path(
                src, self.variables['build directory']))
        return objs

    def __str__(self):
        """ Pretty-print all environment varialbes """
        out_str = ''
        for key in sorted(self.variables):
            out_str += str(key) + ':\n'
            if not hasattr(self.variables[key], '__iter__') or type(self.variables[key]) is str:
                out_str += '    ' + str(self.variables[key]) + '\n'
            else:
                for item in self.variables[key]:
                    out_str += '    ' + str(item) + '\n'
        return out_str

    #------------------------------------------------
    # private

    def _source_to_obj_path(self, src, build_dir):
        src_filename = os.path.basename(src)
        return os.path.join(build_dir, 'obj', src_filename) + '.o'

    def _source_to_dep_path(self, src, build_dir):
        src_filename = os.path.basename(src)
        return os.path.join(build_dir, 'obj', src_filename) + '.d'


def get_compile_cmd_str(src, obj, compiler='gcc', defs=[], includes=[], flags=[]):
    cmd_args = [compiler]
    cmd_args += ['-D' + d for d in defs]
    cmd_args += ['-I' + i for i in includes]
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
    cmd_args += ['-L' + d for d in libdirs]
    if linker_script is not None:
        cmd_args += ['-T' + linker_script]
    cmd_args += ['-o', target]
    cmd_args += objs
    cmd_args += ['-l' + lib for lib in libs]
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


def _arg_list_to_command_string(arg_list):
    return ' '.join([str(arg) for arg in arg_list])
