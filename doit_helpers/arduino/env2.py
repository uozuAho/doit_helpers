""" An improvement over env.py (hopefully) """

import os

from .. import gcc_utils


class ArduinoEnv:

    """ Base arduino environment class """

    # -----------------------------
    # public

    def __init__(self, proj_name, arduino_path, build_dir, hardware):
        self.proj_name = proj_name
        self.arduino_path = arduino_path
        self.build_dir = build_dir
        self.hardware = hardware

    def get_build_tasks(self, sources):
        return []

    def get_upload_task(self, serial_port):
        return []

    # -----------------------------
    # private

    def _source_to_obj_path(self, source):
        """ Get object file output path using source path """
        src_filename = os.path.basename(source)
        return os.path.join(self.core_obj_output_dir, src_filename) + '.o'

    def _source_to_dep_path(self, source):
        """ Get makefile dependency file output path using source path """
        src_filename = os.path.basename(source)
        return os.path.join(self.core_obj_output_dir, src_filename) + '.d'

    def _get_archive_core_objs_tasks(self):
        archive_command = self.archiver + \
            ' rcs ' + self.core_lib_output_path + ' '
        archive_command += ' '.join(self.core_objs)
        return [{
            'name': 'archiving core',
            'actions': [archive_command],
            'targets': [self.core_lib_output_path],
            'file_dep': self.core_objs,
            'clean': True
        }]

    def _get_build_elf_tasks(self, objs, dest):
        return [{
            'name': dest,
            'actions': [gcc_utils.get_link_cmd_str(dest, objs,
                                                   linker=self.linker,
                                                   libdirs=self.ldincludes,
                                                   libs=self.ldlibs,
                                                   flags=self.ldflags)],
            'file_dep': objs,
            'targets': [dest],
            'clean': True
        }]

    def _get_build_eeprom_binary_tasks(self, source, dest):
        objcopy_cmd = ' '.join(
            [self.objcopy] + self.hardware_env.OBJCOPY_EEPROM_FLAGS + [source, dest])
        return [{
            'name': dest,
            'actions': [objcopy_cmd],
            'file_dep': [source],
            'targets': [dest],
            'clean': True
        }]

    def _get_build_flash_binary_tasks(self, source, dest):
        objcopy_cmd = ' '.join(
            [self.objcopy] + self.hardware_env.OBJCOPY_FLASH_FLAGS + [source, dest])
        return [{
            'name': dest,
            'actions': [objcopy_cmd],
            'file_dep': [source],
            'targets': [dest],
            'clean': True
        }]

    def _get_print_size_task(self, binary):
        return [{
            'name': 'size',
            'actions': [self.print_size + ' ' + binary],
            'file_dep': [binary],
            # dummy target makes this always run
            'targets': ['print size'],
            'verbosity': 2,
        }]

    def __str__(self):
        out_str = ''
        for key in dir(self):
            out_str += str(key) + ':\n'
            attr = getattr(self, key)
            if not hasattr(attr, '__iter__') or type(attr) is str:
                out_str += '    ' + str(attr) + '\n'
            else:
                for item in attr:
                    out_str += '    ' + str(item) + '\n'
        return out_str
