import sys

sys.path.append('../..')

from doit_helpers import file_utils
from doit_helpers import gcc_utils

DOIT_CONFIG = {'default_tasks': ['run_exe']}

BUILD_DIR = 'build'
SOURCES = file_utils.find('src', ['*.c'])
OBJS = gcc_utils.get_obj_target_paths(SOURCES, BUILD_DIR)
TARGET = 'example.exe'

gcc_utils.update_env({'c preprocessor defs': ['THINGO_VAL=4']})


def task_compile():
    for task in gcc_utils.get_c_compile_tasks(SOURCES, BUILD_DIR):
        yield task


def task_link():
    for task in gcc_utils.get_link_exe_tasks(OBJS, TARGET):
        yield task


def task_run_exe():
    return {
        'actions': [TARGET],
        'targets': ['run exe'],
        'file_dep': [TARGET],
        'verbosity': 2
    }
