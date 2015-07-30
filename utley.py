# TODO: Allow specifying clean target in a --target chain, i.e., `utley --target=clean,js,css
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

        # Build all targets (assumes an `utley.json` build file).
        utley

        # Specify a different build file than the default `utley.json`.
        utley --config=foo.json

        # Build only the CSS target.
        utley --target=css

        # Build only the JavaScript target.
        utley --target=js

        # Specify multiple targets.
        utley --target=js,css,quizzes

        # Clean.
        utley --clean

        --clean       Run the `clean` build target.
        --config, -c  The location of the build file. Defaults to 'utley.json'.
        --target, -t  Specify build targets (comma-separated)
    '''
    print(textwrap.dedent(str))

def main(argv):
    configFile = 'utley.json'
    doClean = False
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
    if targets:
        for target in targets:
            buildTarget(target, json)
    else:
        # We're building all targets.
        cleanTarget = json.get('clean')

        if cleanTarget:
            clean(cleanTarget)

        for target in json:
            # Skip the clean target!
            if target == 'clean':
                continue

            buildTarget(target, json)

def buildTarget(target, json, isSubTarget=False):
    ls = []
    indent = ''

    if not isinstance(target, dict):
        makeString = bcolors.BOLD + '[INF]' + bcolors.ENDC + ' Making ' + bcolors.OKBLUE + target + bcolors.ENDC + ' target...'

        # Check to see if target is a subtarget (i.e., 'quizzes.chord_buider'). It will only be dot-separated
        # if explicitly passed as a build target.
        if '.' in target:
            print(makeString)
            keys = target.split('.')
            ls = json[keys[0]][keys[1]]

        else:
            if isSubTarget:
                indent = '-----> '

            print(indent + makeString)
            ls = json.get(target)

        # If compressing any of the following targets then send it directly to its same-named compressor.
        if target in ['css', 'js', 'json']:
            compress(ls, target)
        else:
            for subtarget in ls:
                buildTarget(subtarget, ls, True)

    # If a dict then we can't recurse any further, compress the targets and we're done (should only be css
    # and/or js at this point).
    else:
        css = target.get('css')
        if css:
            compress(target.get('css'), 'css')

        js = target.get('js')
        if js:
            compress(target.get('js'), 'js')

def clean(target):
    if not target:
        print(bcolors.FAIL + '[ERROR]:' + bcolors.ENDC + ' Build target does not exist.')
        sys.exit(2)
    else:
        print(bcolors.BOLD + '[INF]' + bcolors.ENDC + ' Making ' + bcolors.OKBLUE + 'clean' + bcolors.ENDC + ' target...')

        for t in target:
            run = t.get('run')

            if not run:
                print('Error: No "run" command, aborting...')
                sys.exit(2)
            else:
                os.system(run)

    print('-----------> ' + bcolors.OKGREEN + 'Done' + bcolors.ENDC + '\n')

def compress(target, compressor):
    print('-----------> Using compressor: ' + bcolors.UNDERLINE + compressor + bcolors.ENDC)

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

