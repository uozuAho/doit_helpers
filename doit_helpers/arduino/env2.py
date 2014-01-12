""" An improvement over env.py (hopefully) """

import glob

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
        self.arduino_core_env.variables[
            'core lib output path'] = build_dir + '/core/core.a'

        self.user_env = gcc_utils.GccEnv(build_dir)
        self.user_env.variables['project name'] = proj_name
        self.user_env.variables.update(hardware_env)
        self.user_env.variables['c source files'] = []
        self.user_env.variables['c++ source files'] = []
        self.user_env.variables['arduino path'] = arduino_path
        self.user_env.variables['elf output'] = build_dir + '/' + proj_name + '.elf'
        self.user_env.variables['bin output'] = build_dir + '/' + proj_name + '.bin'

    def set_c_source_files(self, sources):
        self.user_env.variables['c source files'] = sources

    def set_cpp_source_files(self, sources):
        self.user_env.variables['c++ source files'] = sources

    def add_include_dirs(self, dirs):
        self.user_env.variables['c header search paths'] += dirs
        self.user_env.variables['c++ header search paths'] += dirs

    def set_serial_port(self, serial_port):
        self.user_env.variables['serial_port'] = serial_port

    def get_build_tasks(self):
        elf_output = self.user_env.variables['elf output']
        bin_output = self.user_env.variables['bin output']
        tasks = self._get_build_core_tasks()
        tasks += self.user_env.get_c_compile_tasks()
        tasks += self.user_env.get_cpp_compile_tasks()
        tasks += [self._get_due_link_task(elf_output)]
        tasks += [self._get_create_binary_task(elf_output, bin_output)]
        return tasks

    def get_upload_tasks(self):
        return [self._get_due_upload_task()]

    # -----------------------------
    # private

    def _get_build_core_tasks(self):
        tasks = self.arduino_core_env.get_c_compile_tasks()
        tasks += self.arduino_core_env.get_cpp_compile_tasks()
        tasks += [self._get_archive_core_task()]
        return tasks

    def _get_archive_core_task(self):
        objs = self.arduino_core_env.get_all_objs()
        archiver = self.arduino_core_env.variables['archiver']
        output = self.arduino_core_env.variables['core lib output path']
        archive_command = archiver + ' rcs ' + output + ' ' + ' '.join(objs)
        return {
            'name': output,
            'actions': [archive_command],
            'targets': [output],
            'file_dep': objs,
            'clean': True
        }

    def _get_due_link_task(self, output):
        # Can't use GccEnv link task as the arduino Due link command is rather
        # complicated
        arduino_path = self.user_env.variables['arduino path']
        output_dir = self.user_env.variables['build directory']
        linker = self.user_env.variables['linker']
        flags = self.user_env.variables['linker flags']
        script = self.user_env.variables['linker script']
        core = self.arduino_core_env.variables['core lib output path']
        link_map = output_dir + '/' + self.user_env.variables['project name'] + '.map'

        cmd_args = [linker] + flags
        cmd_args += [
            '-T' + script,
            '-Wl,-Map,' + link_map,
            '-o',
            output,
        ]

        cmd_args += ['-Wl,--start-group']
        cmd_args += glob.glob(self.arduino_core_env.variables['build directory'] + '/obj/syscalls*.o')
        cmd_args += self.user_env.get_all_objs()
        cmd_args += [arduino_path + '/hardware/arduino/sam/variants/arduino_due_x/libsam_sam3x8e_gcc_rel.a']
        cmd_args += [core]
        cmd_args += ['-Wl,--end-group']

        link_cmd = ' '.join(cmd_args)

        return {
            'name': output,
            'actions': [link_cmd],
            'file_dep': self.user_env.get_all_objs(),
            'targets': [output],
            'clean': True
        }

    def _get_create_binary_task(self, input, output):
        objcopy = self.user_env.variables['objcopy']
        cmd = ' '.join([objcopy, '-O binary', input, output])
        return {
            'name': output,
            'actions': [cmd],
            'file_dep': [input],
            'targets': [output],
            'clean': True
        }

    def _get_due_upload_task(self):
        arduino_path = self.user_env.variables['arduino path']
        uploader = arduino_path + '/hardware/tools/bossac.exe'
        serial_port = self.user_env.variables['serial_port']
        cmd_args = [
            uploader,
            '--port=' + serial_port,
            '-U false -e -w -v -b',
            self.user_env.variables['bin output'],
            '-R'
        ]
        return {
            'name': 'upload',
            # TODO: the following is Windows-only.
            # Linux version is:
            # stty -F /dev/${PORT} raw ispeed 1200 ospeed 1200
            # then bossac
            'actions': ['mode ' + serial_port + ':1200,n,8,1',
                        'timeout /T 2',
                        ' '.join(cmd_args)],
            'file_dep': [self.user_env.variables['bin output']],
            'verbosity': 2
        }

    def _add_arduino_library_source(self):
        """ Search user source code for arduino libraries to
            include into the build environment
        """
        # TODO: this
        pass

    def _get_incl_sys_headers(self, path):
        """ Return a list of <> includes in the given file """
        # TODO: needed for adding arduino libraries
        pass


def get_hardware_env(arduino_path, hardware):
    if hardware.lower() == 'uno':
        env = env_uno.get_env(arduino_path)
    elif hardware.lower() == 'due':
        env = env_due.get_env(arduino_path)
    else:
        raise Exception('Unknown hardware type: ' + hardware)

    return env
