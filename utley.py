import base_compress
from bcolors import bcolors
import compressors.css
import compressors.js
import getopt
import os
import sys
import textwrap

def usage():
    str = '''
        USAGE:

        # Build all targets (assumes an utley.json build file).
        utley

        # Specify a different build file.
        utley --config=foo.json

        # Build only the CSS target.
        utley --target=css

        # Build only the JavaScript target.
        utley --target=js

        # Build only multiple target.
        utley --target=js,css,quizzes

        # Clean.
        utley --clean

        --clean       Run the clean build target.
        --config, -c  The location of the build file. Defaults to 'utley.json'.
        --css         Build the CSS only.
        --js          Build the JavaScript only.
    '''
    print(textwrap.dedent(str))

def main(argv):
    doClean = False
    configFile = 'utley.json'
    css = []
    js = []
    targets = None

    # If there are no given arguments, assume an utley.json file and both build targets.
    if len(argv) == 0:
        json = base_compress.getJson()
    else:
        try:
            opts, args = getopt.getopt(argv, 'hc:t:', ['help', 'config=', 'clean', 'target='])
        except getopt.GetoptError:
            print('Error: Unrecognized flag.')
            usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
                sys.exit(0)
            elif opt in ('-c', '--config'):
                configFile = arg
            elif opt == '--clean':
                doClean = True
            elif opt in ('-t', '--target'):
                targets = base_compress.make_list(arg)

        json = base_compress.getJson(configFile)

    if not doClean:
        build(json, targets)
    else:
        clean(json.get('clean'))

def build(json={}, targets=None):
    # If compressing any of the following source files, it's not necessary to
    # explcitly define the compressor in the build file.
    defaults = {
        'css': 'css',
        'js': 'js',
        'json': 'css'
    }

    if targets:
        for target in targets:
            buildTarget(target, json, defaults)
    else:
        cleanTarget = json.get('clean')
        if cleanTarget:
            clean(cleanTarget)

        for target in json:
            # Skip the clean target!
            if target == 'clean':
                continue

            buildTarget(target, json, defaults)

def buildTarget(target, json, defaults):
    print(bcolors.BOLD + '[INF]' + bcolors.ENDC + ' Making ' + target +  ' target...')

    if target in defaults:
        compress(json.get(target), defaults[target])
    else:
        # Redefine target to be the list target.
        target = json.get(target)

        for targ in target:
            print('-----> ' + bcolors.BOLD + '[INF]' + bcolors.ENDC + ' Making ' + targ +  ' subtarget:')
            ls = target.get(targ)

            for d in ls:
                compress(d.get('css'), 'css')
                compress(d.get('js'), 'js')

def clean(target):
    if not target:
        print(bcolors.FAIL + '[ERROR]:' + bcolors.ENDC + ' Build target does not exist.')
        sys.exit(2)
    else:
        print('\n**********************************')
        print(bcolors.BOLD + '[INF]' + bcolors.ENDC + ' Making clean target...')
        for t in target:
            run = t.get('run')

            if not run:
                print('Error: No "run" command, aborting...')
                sys.exit(2)
            else:
                os.system(run)

    print('-----------> ' + bcolors.OKGREEN + 'Done' + bcolors.ENDC + '\n')

def compress(target, compressor):
    print('-----------> Using compressor: ' + compressor)
    for t in target:
        src = t.get('src')
        output = t.get('output')
        dest = t.get('dest', '.')
        version = t.get('version', '')
        dependencies = t.get('dependencies', [])
        exclude = t.get('exclude', [])

        if compressor == 'css' or compressor == 'json':
            compressors.css.compress(src, output, dest, version, dependencies, exclude)
        elif compressor == 'js':
            compressors.js.compress(src, output, dest, version, dependencies, exclude)


    print('-----------> '+ bcolors.OKGREEN + 'Done' + bcolors.ENDC + '\n')

if __name__ == '__main__':
#    if len(sys.argv) == 1:
#        usage()
#        sys.exit(2)

    main(sys.argv[1:])

