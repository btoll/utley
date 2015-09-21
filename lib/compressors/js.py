import lib.base
from lib.bcolors import bcolors
import itertools
import os
import subprocess
import sys

def compress(compressor, src, verbose=False, silent=False):
    if not src:
        print('Error: You must provide the location of the source files.')
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

        return subprocess.getoutput(compressor + ' ' + src)

    except (KeyboardInterrupt, EOFError):
        # Control-C or Control-D sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

