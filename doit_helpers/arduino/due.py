COMMON_COMPILE_FLAGS = [
    '-c',
    '-g',
    '-Os',
    '-Wall',
    '-ffunction-sections',
    '-fdata-sections',
    '-mmcu=atmega328p',
    '-MMD',
]

C_FLAGS = COMMON_COMPILE_FLAGS + [
    '-x c',     # ensure c files are processed as c files!
]

C_DEFS = [
    'F_CPU=16000000L',
    'USB_VID=null',
    'USB_PID=null',
    'ARDUINO=105',
]

CPP_FLAGS = COMMON_COMPILE_FLAGS + [
    '-fno-exceptions',
    '-x c++',     # stops .ino files being processed as objects
]

CPP_DEFS = C_DEFS

LINKER_FLAGS = [
    '-Os',
    '-Wl,--gc-sections',
    '-mmcu=atmega328p',
]

LINKER_LIBS = [
    'm'
]

OBJCOPY_EEPROM_FLAGS = [
    '-O',
    'ihex',
    '-j',
    '.eeprom',
    '--set-section-flags=.eeprom=alloc,load',
    '--no-change-warnings',
    '--change-section-lma',
    '.eeprom=0',
]

OBJCOPY_FLASH_FLAGS = [
    '-O',
    'ihex',
    '-R',
    '.eeprom',
]

AVRDUDE_FLAGS = [
    '-patmega328p',
    '-carduino',
    '-b115200',
    '-D'
]
