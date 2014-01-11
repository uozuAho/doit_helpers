""" An improvement over env.py (hopefully) """

from .. import gcc_utils
import env_uno
import env_due


class ArduinoEnv():

    """ Base arduino environment class """

    # -----------------------------
    # public

    def __init__(self, proj_name, build_dir, arduino_path, hardware):
        hardware_env = get_hardware_env(arduino_path, hardware)

        self.arduino_core_env = gcc_utils.GccEnv(build_dir + '/core')
        self.arduino_core_env.variables.update(hardware_env)

        self.user_env = gcc_utils.GccEnv(build_dir)
        self.user_env.variables['project name'] = proj_name
        self.user_env.variables.update(hardware_env)

    def set_c_source_files(self, sources):
        self.user_env.variables['c source files'] = sources

    def set_cpp_source_files(self, sources):
        self.user_env.variables['c++ source files'] = sources

    def set_include_dirs(self, dirs):
        self.user_env.variables['c header search paths'] = dirs
        self.user_env.variables['c++ header search paths'] = dirs

    def get_build_tasks(self):
        return self._get_build_core_tasks()

    def get_upload_tasks(self, serial_port):
        return []

    # -----------------------------
    # private

    def _get_build_core_tasks(self):
        tasks = self.arduino_core_env.get_c_compile_tasks()
        tasks += self.arduino_core_env.get_cpp_compile_tasks()
        return tasks


def get_hardware_env(arduino_path, hardware):
    if hardware.lower() == 'uno':
        env = env_uno.get_env(arduino_path)
    elif hardware.lower() == 'due':
        env = env_due.get_env(arduino_path)
    else:
        raise Exception('Unknown hardware type: ' + hardware)

    return env
