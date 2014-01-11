from .. import file_utils


def get_env(arduino_path):

    bin_dir = arduino_path + '/hardware/tools/avr/bin/'

    return {
        # -------------------------------
        # c
        # -------------------------------
        'c compiler': bin_dir + 'avr-gcc',

        'c preprocessor defs': [
            'F_CPU=16000000L',
            'USB_VID=null',
            'USB_PID=null',
            'ARDUINO=105',
        ],

        'c compiler flags': [
            '-c',
            '-g',
            '-Os',
            '-Wall',
            '-ffunction-sections',
            '-fdata-sections',
            '-mmcu=atmega328p',
            '-MMD',
            '-x c',     # ensure c files are processed as c files!
        ],

        'c header search paths': [],

        'c source files': file_utils.find(
            arduino_path + '/hardware/arduino/cores/arduino',
            ['*.c'], search_subdirs=True),

        # -------------------------------
        # c++
        # -------------------------------
        'c++ compiler': bin_dir + 'avr-g++',

        'c++ preprocessor defs': [
            'F_CPU=16000000L',
            'USB_VID=null',
            'USB_PID=null',
            'ARDUINO=105',
        ],

        'c++ compiler flags': [
            '-c',
            '-g',
            '-Os',
            '-Wall',
            '-ffunction-sections',
            '-fdata-sections',
            '-mmcu=atmega328p',
            '-MMD',
            '-fno-exceptions',
            '-x c++',     # stops .ino files being processed as objects
        ],

        'c++ header search paths': [],

        'c++ source files': file_utils.find(
            arduino_path + '/hardware/arduino/cores/arduino',
            ['*.cpp'], search_subdirs=True),

        # -------------------------------
        # linker
        # -------------------------------
        'linker': bin_dir + 'avr-gcc',

        'linker script': None,

        'linker libraries': [
            'm'
        ],

        'linker flags': [
            '-Os',
            '-Wl,--gc-sections',
            '-mmcu=atmega328p',
        ],

        'linker library search paths': [],

        # -------------------------------
        # objcopy
        # -------------------------------
        'objcopy': bin_dir + 'avr-objcopy',

        'objcopy eeprom flags': [
            '-O',
            'ihex',
            '-j',
            '.eeprom',
            '--set-section-flags=.eeprom=alloc,load',
            '--no-change-warnings',
            '--change-section-lma',
            '.eeprom=0',
        ],

        'objcopy flash flags': [
            '-O',
            'ihex',
            '-R',
            '.eeprom',
        ],

        # -------------------------------
        # other bits
        # -------------------------------
        'archiver': bin_dir + 'avr-ar',
        'print size': bin_dir + 'avr-size',
    }
