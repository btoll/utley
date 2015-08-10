# TODO: support compressors other than YUI Compressor?
import base_compress
from bcolors import bcolors
import getopt
import itertools
import os
import server
import subprocess
import sys
import textwrap

builds = {}

def usage():
    str = '''
        USAGE:

            CLI:
                python3 js_compress.py -s /usr/local/www/PeteJS/src/ -d /usr/local/www/owlsnestfarm/build/ -o pete.js --dependencies 'Pete.prototype.js, Pete.js, Pete.Element.js, Pete.Composite.js, Pete.Observer.js'

            As an imported module:
                js_compress.compress(src[, output='min.js', dest='.', version='3.0.0', dependencies='', exclude='', jar=None])

        --src, -s       The location of the JavaScript source files, must be specified.
                        If a list, concatenate all entries into one file.
                        If this is a path value, rather than just a filename, the value will be split with the basename becoming the new value and the path value becoming the value for dest.
        --output, -o    The name of the new minimized file, defaults to 'min.js'.
        --dest, -d      The location where the minified file will be moved, defaults to cwd.
        --version, -v   The version of the minified script.
        --dependencies  Any number of directories or filenames, separated by a comma, defaults to an empty list. FIFO.
                        The absolute path will be prepended to the element, depends on the src location.
        --exclude       Any number of directories or filenames, separated by a comma, that should be excluded in the build, defaults to an empty list.
                        The absolute path will be prepended to the element, depends on the src location.
        --jar, -j       The location of the jar file, defaults to the value of YUICOMPRESSOR environment variable.
    '''
    print(textwrap.dedent(str))

def main(argv):
    jar = None
    dest = '.'
    src = ''
    output = 'min.js'
    version = ''
    dependencies = []
    exclude = []
    # Note this needs to be defined to support full build tool.
    name = ''

    try:
        opts, args = getopt.getopt(argv, 'hs:o:d:v:j:', ['help', 'src=', 'output=', 'dest=', 'version=', 'dependencies=', 'exclude=', 'jar='])
    except getopt.GetoptError:
        print('Error: Unrecognized flag.')
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt in ('-s', '--src'):
            src = arg
        elif opt in ('-o', '--output'):
            output = arg
        elif opt in ('-v', '--version'):
            version = arg
        elif opt in ('-d', '--dest'):
            dest = arg
        elif opt == '--dependencies':
            dependencies = arg
        elif opt == '--exclude':
            exclude = arg
        elif opt in ('-j', '--jar'):
            jar = arg

    compress(src, output, dest, version, dependencies, exclude, name, verbose, jar)

def compress(src, output='min.js', dest='.', version='', dependencies=[], exclude=[], name='', verbose=False, jar=None):
    global builds

    if not src:
        print('Error: You must provide the location of the source files.')
        sys.exit(2)

    if not jar:
        # Provide an alternate location to the jar to override the environment variable (if set).
        jar = os.getenv('YUICOMPRESSOR')
        if not jar:
            jar = input('Location of YUI Compressor jar (set a YUICOMPRESSOR environment variable to skip this step): ')
            if not jar:
                print('Error: You must provide the location of YUI Compressor jar.')
                sys.exit(2)

    try:
        buff = []
        ls = base_compress.sift_list(
            base_compress.make_list(src),
            'js',
            base_compress.make_list(exclude),
            base_compress.make_list(dependencies)
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
                    sys.stdout.flush()
                    sys.stdout.write('\b')
                else:
                    print(bcolors.ON_BLUE + bcolors.BROWN + '[DEBUG]' + bcolors.ON_WHITE + bcolors.YELLOW + ' Processing -> ' + bcolors.ENDC + script)

                buff.append(subprocess.getoutput('java -jar ' + jar + ' ' + script))

        if name:
            builds.update({
                name: buff
            })

        base_compress.write_buffer(buff, output)

    except (KeyboardInterrupt, EOFError):
        # Control-C or Control-D sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    main(sys.argv[1:])

