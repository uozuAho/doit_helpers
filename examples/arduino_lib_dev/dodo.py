import glob
import os
import sys

sys.path.append('../..')
from doit_helpers.arduino import env2 as arduino_env

# DOIT_CONFIG = {'default_tasks': ['build_exe']}

# ---------------------------------------------------------------------
# Build settings

PROJECT_NAME = 'arduino_lib'

BUILD_DIR = 'build'

OBJ_DIR = os.path.join(BUILD_DIR, 'obj')

ARDUINO_ROOT = 'D:\\programs_win\\arduino-1.0.5'

SERIAL_PORT = 'COM5'

INCLUDE_DIRS = [
    PROJECT_NAME,
]

C_SOURCES = glob.glob(PROJECT_NAME + '/**/*.c')

CPP_SOURCES = glob.glob(PROJECT_NAME + '/**/*.cpp')
CPP_SOURCES += glob.glob(PROJECT_NAME + '/**/*.ino')

# Manually add source files (ADD LIBRARY EXAMPLE HERE)
CPP_SOURCES += [PROJECT_NAME + '/examples/goggles/goggles.pde']

# Configure the arduino environment
ARDUINO_ENV_UNO = arduino_env.ArduinoEnv(
    PROJECT_NAME, BUILD_DIR, ARDUINO_ROOT, 'uno')

ARDUINO_ENV_UNO.set_c_source_files(C_SOURCES)
ARDUINO_ENV_UNO.set_cpp_source_files(CPP_SOURCES)
ARDUINO_ENV_UNO.set_include_dirs(INCLUDE_DIRS)

# ---------------------------------------------------------------------

# print '+++++++++++++++++++++++++++++++++++++++++'
# print 'user env:'
# print ARDUINO_ENV_UNO.user_env
# print '+++++++++++++++++++++++++++++++++++++++++'
# print 'core env:'
# print ARDUINO_ENV_UNO._arduino_core_env


def task_build():
    for task in ARDUINO_ENV_UNO.get_build_tasks():
        yield task
