# TODO: support compressors other than YUI Compressor?
import lib.base
from lib.bcolors import bcolors
import itertools
import os
import subprocess
import sys

def compress(src, version='', verbose=False, silent=False, jar=None):
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
        if not silent and not verbose:
            spinner = itertools.cycle(['-', '\\', '|', '/'])

        if not silent and not verbose:
            sys.stdout.write(next(spinner))
            sys.stdout.write('\b')
            sys.stdout.flush()
            sys.stdout.write('\b')
        elif verbose:
            print(bcolors.ON_BLUE + bcolors.BROWN + '[DEBUG]' + bcolors.ON_WHITE + bcolors.YELLOW + ' Processing -> ' + bcolors.ENDC + script)

        return subprocess.getoutput('uglifyjs ' + src)
        #return subprocess.getoutput('java -jar ' + jar + ' ' + src)

    except (KeyboardInterrupt, EOFError):
        # Control-C or Control-D sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

