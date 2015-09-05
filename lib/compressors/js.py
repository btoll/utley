# TODO: support compressors other than YUI Compressor?
import lib.base
from lib.bcolors import bcolors
import itertools
import os
import subprocess
import sys

builds = {}

def compress(src, output='min.js', dest='.', version='', dependencies=[], exclude=[], name='', verbose=False, jar=None):
    global builds

    if not src:
        print('Error: You must provide the location of the source files.')
        sys.exit(1)

    if not jar:
        # Provide an alternate location to the jar to override the environment variable (if set).
        jar = os.getenv('YUICOMPRESSOR')
        if not jar:
            jar = input('Location of YUI Compressor jar (set a YUICOMPRESSOR environment variable to skip this step): ')
            if not jar:
                print('Error: You must provide the location of YUI Compressor jar.')
                sys.exit(1)

    try:
        buff = []
        ls = lib.base.sift_list(
            lib.base.make_list(src),
            'js',
            lib.base.make_list(exclude),
            lib.base.make_list(dependencies)
        )

        if not verbose:
            spinner = itertools.cycle(['-', '\\', '|', '/'])

        for script in ls:
            # If script is a named target then retrieve it from the global `builds` dict.
            # Note that it assumes the named target was already built!
            if script[0] == '@':
                buff.append(''.join(builds.get(script[1:])))
            else:
                if not verbose:
                    sys.stdout.write(next(spinner))
                    sys.stdout.write('\b')
                    sys.stdout.flush()
                    sys.stdout.write('\b')
                else:
                    print(lib.bcolors.ON_BLUE + lib.bcolors.BROWN + '[DEBUG]' + lib.bcolors.ON_WHITE + lib.bcolors.YELLOW + ' Processing -> ' + lib.bcolors.ENDC + script)

                buff.append(subprocess.getoutput('babel ' + script + ' | java -jar ' + jar + ' --type js'))

        if name:
            builds.update({
                name: buff
            })

        lib.base.write_buffer(buff, output)

    except (KeyboardInterrupt, EOFError):
        # Control-C or Control-D sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

