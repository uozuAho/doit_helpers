import unittest
import sys
sys.path.append('..')

from doit_helpers import gcc_utils


class GccDepfileParsingTestCase(unittest.TestCase):

    test_file_1 = 'test_data/gcc_dep_files/WString.cpp.d'
    test_file_1_exp_output = {
        'build/core\obj\WString.cpp.o': [
            'D:/programs_win/arduino-1.5.2/hardware/arduino/sam/cores/arduino\WString.cpp',
            'D:/programs_win/arduino-1.5.2/hardware/arduino/sam/cores/arduino\/WString.h',
            'D:/programs_win/arduino-1.5.2/hardware/arduino/sam/cores/arduino\/itoa.h'
        ]
    }

    def test_parse_file(self):
        deps = gcc_utils.read_dependency_file(self.test_file_1)
        self.assertEqual(sorted(self.test_file_1_exp_output.keys()),
                         sorted(deps.keys()))
        for key in deps.keys():
            self.assertEqual(sorted(deps[key]),
                             sorted(self.test_file_1_exp_output[key]))
