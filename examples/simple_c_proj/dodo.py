import sys

sys.path.append('../..')

from doit_helpers import file_utils
from doit_helpers import gcc_utils

DOIT_CONFIG = {'default_tasks': ['run_exe']}

BUILD_DIR = 'build'
SOURCES = file_utils.find('src', ['*.c'])
TARGET = 'example.exe'

gcc_env = gcc_utils.GccEnv(BUILD_DIR)
gcc_env.variables['c preprocessor defs'].append('THINGO_VAL=4')
gcc_env.variables['c source files'] = SOURCES


def task_build():
    tasks = gcc_env.get_c_compile_tasks()
    tasks += gcc_env.get_link_exe_tasks(TARGET)
    for task in tasks:
        yield task


def task_run_exe():
    return {
        'actions': [TARGET],
        'targets': ['run exe'],
        'file_dep': [TARGET],
        'verbosity': 2
    }
