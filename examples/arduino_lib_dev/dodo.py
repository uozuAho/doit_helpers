import os
import sys
from doit.tools import create_folder

sys.path.append('../..')
from doit_helpers.arduino import env as arduino_env
from doit_helpers import file_utils
from doit_helpers import gcc_utils

DOIT_CONFIG = {'default_tasks': ['build_exe']}

# ---------------------------------------------------------------------
# Build settings

PROJECT_NAME = 'arduino_lib'

BUILD_DIR = 'build'

OBJ_DIR = os.path.join(BUILD_DIR, 'obj')

ARDUINO_ROOT = 'D:\\programs_win\\arduino-1.0.5'

ARDUINO_ENV = arduino_env.ArduinoEnv(PROJECT_NAME, ARDUINO_ROOT, BUILD_DIR, 'uno')

SERIAL_PORT = 'COM5'

INCLUDE_DIRS = [
    'arduino_lib',
]

INCLUDE_DIRS += ARDUINO_ENV.cincludes

SOURCE_DIRS = [
    'arduino_lib',
]


def src_to_obj_path(src_path):
    """ Source file path to object file path conversion """
    return os.path.join(OBJ_DIR, os.path.basename(src_path) + '.o')


def src_to_dep_path(src_path):
    """ Source file path to dependency file path conversion """
    return os.path.join(OBJ_DIR, os.path.basename(src_path) + '.d')

# Add all source files from SOURCE DIRS
C_SOURCES = []
CPP_SOURCES = []
for path in SOURCE_DIRS:
    C_SOURCES += file_utils.find(path, '*.c')
    CPP_SOURCES += file_utils.find(path, ['*.cpp', '*.ino'])

# Manually add source files (ADD LIBRARY EXAMPLE HERE)
CPP_SOURCES += ['arduino_lib/examples/goggles/goggles.pde']

# C source file dependency map
DEPS = gcc_utils.get_dependency_dict(BUILD_DIR)


# ---------------------------------------------------------------------
# utilities

def get_source_dependencies(source):
    obj = src_to_obj_path(source)
    if obj in DEPS:
        return DEPS[obj]
    else:
        return [source]


def get_c_compile_command_str(source, obj):
    return gcc_utils.get_compile_cmd_str(source, obj,
                                         compiler=ARDUINO_ENV.c_compiler,
                                         defs=ARDUINO_ENV.cdefs,
                                         includes=INCLUDE_DIRS,
                                         flags=ARDUINO_ENV.cflags)


def get_cpp_compile_command_str(source, obj):
    return gcc_utils.get_compile_cmd_str(source, obj,
                                         compiler=ARDUINO_ENV.cpp_compiler,
                                         defs=ARDUINO_ENV.cppdefs,
                                         includes=INCLUDE_DIRS,
                                         flags=ARDUINO_ENV.cppflags)


# ---------------------------------------------------------------------
# tasks

def task_build_arduino_core():
    for task in ARDUINO_ENV.get_build_core_tasks():
        yield task


def task_compile_c():
    for source in C_SOURCES:
        obj = src_to_obj_path(source)
        dep = src_to_dep_path(source)
        yield {
            'name': obj,
            'actions': [(create_folder, [os.path.dirname(obj)]),
                        get_c_compile_command_str(source, obj)],
            'targets': [obj, dep],
            'file_dep': get_source_dependencies(source),
            'clean': True
        }


def task_compile_cpp():
    for source in CPP_SOURCES:
        obj = src_to_obj_path(source)
        dep = src_to_dep_path(source)
        yield {
            'name': obj,
            'actions': [(create_folder, [os.path.dirname(obj)]),
                        get_cpp_compile_command_str(source, obj)],
            'targets': [obj, dep],
            'file_dep': get_source_dependencies(source),
            'clean': True
        }


def task_build_exe():
    objs = [src_to_obj_path(x) for x in C_SOURCES]
    objs += [src_to_obj_path(x) for x in CPP_SOURCES]
    objs += [ARDUINO_ENV.core_lib_output_path]
    for task in ARDUINO_ENV.get_build_exe_tasks(PROJECT_NAME, objs):
        yield task


def task_upload():
    return ARDUINO_ENV.get_upload_task(SERIAL_PORT)


if __name__ == '__main__':
    ARDUINO_ENV.get_build_core_tasks()
    print ARDUINO_ENV
