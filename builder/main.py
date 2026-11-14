import os, sys, glob
from SCons.Script import DefaultEnvironment, Default
#Import('env')
env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
framework = os.path.join(platform.get_dir(), 'framework')
core = os.path.join(framework, 'cores', 'arduino')
variant_name = board.get('build.variant')
variant = os.path.join(framework, 'variants', variant_name)
ldscript = board.get('build.ldscript')
if not os.path.isfile(os.path.join(variant, 'linker', ldscript)):
    raise RuntimeError('Missing variant/linker for %s. Run scripts/install_variants.py with the full mcx-arduino-core checkout.' % variant_name)
cc = platform.get_package_dir('toolchain-gccarmnoneeabi')
if not cc: raise RuntimeError('ARM GCC package not installed')
env.PrependENVPath('PATH', os.path.join(cc, 'bin'))
env.Replace(CC='arm-none-eabi-gcc', CXX='arm-none-eabi-g++', AS='arm-none-eabi-gcc', AR='arm-none-eabi-ar', RANLIB='arm-none-eabi-ranlib', OBJCOPY='arm-none-eabi-objcopy', SIZE='arm-none-eabi-size', PROGSUFFIX='.elf')
flags=['-mcpu='+board.get('build.mcu')] + board.get('build.fpu_flags', []) + ['-mthumb']
defines=['PRINTF_FLOAT_ENABLE=1','SCANF_FLOAT_ENABLE=1','PRINTF_ADVANCED_ENABLE=1','SCANF_ADVANCED_ENABLE=1','__NEWLIB__','SDK_OS_BAREMETAL','SERIAL_PORT_TYPE_UART=1','SDK_DEBUGCONSOLE=0','__USE_CMSIS','ARDUINO=10819','ARDUINO_ARCH_MCX','ARDUINO_'+board.get('build.board_macro'),'F_CPU='+str(board.get('build.f_cpu')),'MCX_ARDUINO_CORE_VERSION_MAJOR=0','MCX_ARDUINO_CORE_VERSION_MINOR=10','MCX_ARDUINO_CORE_VERSION_PATCH=0','SDK_DELAY_USE_DWT',*[(x[2:] if x.startswith('-D') else x) for x in board.get('build.board_defines', [])]]
common=board.get('build.opt_flags', ['-O2'])+['-fno-common','-g3','-gdwarf-5','-ffunction-sections','-fdata-sections','-fno-builtin','-fmerge-constants','-specs=nano.specs']
includes=[core,os.path.join(core,'sdk'),os.path.join(core,'r01lib'),os.path.join(core,'arduino_api'),os.path.join(variant,'include')]
env.Append(CPPPATH=includes,CPPDEFINES=defines,CCFLAGS=flags+common, CFLAGS=['-Wall','-Wno-unused-parameter','-Wno-missing-field-initializers','-Wno-old-style-declaration','-fstack-usage'], CXXFLAGS=['-Wall','-Wno-address-of-packed-member','-Wno-unused-parameter','-Wno-missing-field-initializers','-std=c++20','-fno-rtti','-fno-exceptions','-fno-threadsafe-statics','-fstack-usage'], ASFLAGS=flags+['-x','assembler-with-cpp'], LINKFLAGS=flags+['-nostdlib','-Wl,--gc-sections','-Wl,--print-memory-usage','-Wl,--sort-section=alignment','-Wl,-u,_printf_float','-Wl,-u,_scanf_float','-T'+os.path.join(variant,'linker',ldscript)], LIBS=['c','m','gcc'])
# Build the Arduino core as a single archive; force all objects into final ELF.
# Exclude test/example files and use the same recursive source groups as the IDE.
source_dirs=[core,os.path.join(core,'arduino_api'),os.path.join(core,'r01lib'),os.path.join(core,'sdk'),os.path.join(variant,'src')]
objects=[]
for idx, directory in enumerate(source_dirs):
    for src in sorted(glob.glob(os.path.join(directory,'*'))):
        if os.path.isfile(src) and src.endswith(('.c','.cpp','.S','.s')):
            obj=env.Object(os.path.join('$BUILD_DIR','mcxcore',str(idx),os.path.basename(src)+'.o'),src)
            objects.extend(obj)
corelib=env.Library(os.path.join('$BUILD_DIR','libmcxcore'),objects)
# BuildSources registers object nodes in PIOBUILDFILES; its return value is None.
env.BuildSources(os.path.join('$BUILD_DIR', 'src'), '$PROJECT_SRC_DIR')
project_objects = env.get('PIOBUILDFILES', [])
if not project_objects:
    raise RuntimeError('No project objects found. Check src/main.cpp and build_src_filter.')

# Link only the core archive members referenced by the project; this is
# necessary for the smaller MCXA153 and MCXC444 flash sizes.
env.Replace(
    LINKCOM=(
        '$CXX -o "$TARGET" $SOURCES '
        '"' + str(corelib[0]) + '" $LINKFLAGS -lc -lm -lgcc'
    )
)
elf = env.Program(os.path.join('$BUILD_DIR', 'firmware'), project_objects)
env.Depends(elf, corelib)
binary = env.Command(
    os.path.join('$BUILD_DIR', 'firmware.bin'), elf,
    '$OBJCOPY -O binary $SOURCE $TARGET'
)
Default(elf, binary)
python=sys.executable
uploader=os.path.join(platform.get_dir(),'scripts','upload.py')
env.Replace(UPLOADCMD='"'+python+'" "'+uploader+'" "$BUILD_DIR/firmware.elf" "'+board.get('upload.linkserver_target')+'"')
env.AddCustomTarget('upload',elf,env.subst('$UPLOADCMD'),title='Upload with NXP LinkServer')
