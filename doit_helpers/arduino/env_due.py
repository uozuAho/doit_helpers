import glob


def get_env(arduino_path):

    bin_dir = arduino_path + '/hardware/tools/g++_arm_none_eabi/bin/'

    return {
        # -------------------------------
        # c
        # -------------------------------
        'c compiler': bin_dir + 'arm-none-eabi-gcc',

        'c preprocessor defs': [
            'printf=iprintf',
            'F_CPU=84000000L',
            'ARDUINO=152',
            '__SAM3X8E__',
            'USB_PID=0x003e',
            'USB_VID=0x2341',
            'USBCON',
        ],

        'c compiler flags': [
            '-c',
            '-g',
            '-Os',
            '-Wall',
            '-w',
            '-ffunction-sections',
            '-fdata-sections',
            '-nostdlib',
            '--param max-inline-insns-single=500',
            '-mcpu=cortex-m3',
            '-mthumb',
            '-MMD',
            '-x c',     # ensure c files are processed as c files!
        ],

        'c header search paths': [
            arduino_path + '/hardware/arduino/sam/system/libsam',
            arduino_path + '/hardware/arduino/sam/system/CMSIS/CMSIS/Include/',
            arduino_path + '/hardware/arduino/sam/system/CMSIS/Device/ATMEL/',
            arduino_path + '/hardware/arduino/sam/cores/arduino',
            arduino_path + '/hardware/arduino/sam/variants/arduino_due_x',
        ],

        'c source files': glob.glob(arduino_path + '/hardware/arduino/sam/cores/arduino/*.c'),

        # -------------------------------
        # c++
        # -------------------------------
        'c++ compiler': bin_dir + 'arm-none-eabi-g++',

        'c++ preprocessor defs': [
            'printf=iprintf',
            'F_CPU=84000000L',
            'ARDUINO=152',
            '__SAM3X8E__',
            'USB_PID=0x003e',
            'USB_VID=0x2341',
            'USBCON',
        ],

        'c++ compiler flags': [
            '-c',
            '-g',
            '-Os',
            '-w',
            '-Wall',
            '-ffunction-sections',
            '-fdata-sections',
            '-nostdlib',
            '--param max-inline-insns-single=500',
            '-fno-rtti',
            '-fno-exceptions',
            '-mcpu=cortex-m3',
            '-mthumb',
            '-MMD',
            '-x c++',     # stops .ino files being processed as objects
        ],

        'c++ header search paths': [
            arduino_path + '/hardware/arduino/sam/system/libsam',
            arduino_path + '/hardware/arduino/sam/system/CMSIS/CMSIS/Include/',
            arduino_path + '/hardware/arduino/sam/system/CMSIS/Device/ATMEL/',
            arduino_path + '/hardware/arduino/sam/cores/arduino',
            arduino_path + '/hardware/arduino/sam/variants/arduino_due_x',
        ],

        'c++ source files': glob.glob(arduino_path + '/hardware/arduino/sam/cores/arduino/*.cpp') +
                            glob.glob(arduino_path + '/hardware/arduino/sam/variants/arduino_due_x/variant.cpp'),

        # -------------------------------
        # linker
        # -------------------------------
        'linker': bin_dir + 'arm-none-eabi-g++',

        'linker script': arduino_path + '/hardware/arduino/sam/variants/arduino_due_x/linker_scripts/gcc/flash.ld',

        'linker libraries': [
            'm',
            'gcc'
        ],

        'linker flags': [
            '-Os',
            '-Wl,--gc-sections',
            '-mcpu=cortex-m3',
            '-mthumb',
            '-Wl,--cref',
            '-Wl,--check-sections',
            '-Wl,--gc-sections',
            '-Wl,--entry=Reset_Handler',
            '-Wl,--unresolved-symbols=report-all',
            '-Wl,--warn-common',
            '-Wl,--warn-section-align',
            '-Wl,--warn-unresolved-symbols',
        ],

        'linker library search paths': [],

        # -------------------------------
        # objcopy
        # -------------------------------
        'objcopy': bin_dir + 'arm-none-eabi-objcopy',

        'objcopy flags': [
            '-O',
            'binary',
        ],

        # -------------------------------
        # other bits
        # -------------------------------
        'archiver': bin_dir + 'arm-none-eabi-ar',
    }
