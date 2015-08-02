# TODO: Add global var for visual spacing '******'
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

        # Build multiple targets.
        utley --target=js,css,quizzes

        # Build a nested subtarget.
        utley --target=foo.bar.quux

        # Build whatever you want.
        utley --target=clean,css,quizzes.chord_builder,my_custom_target

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
        print(bcolors.BOLD + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.OKBLUE + 'clean' + bcolors.ENDC + ' target...')

        clean(json.get('clean'))

def build(json={}, targets=None):
    if targets:
        for target in targets:
            buildTarget(target, json)
    else:
        # We're building all targets.
        cleanTarget = json.get('clean')

        if cleanTarget:
            print(bcolors.BOLD + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.OKBLUE + 'clean' + bcolors.ENDC + ' target...')

            clean(cleanTarget)

        for target in json:
            # Skip the clean target!
            if target == 'clean':
                continue

            buildTarget(target, json)

def buildTarget(target, json, indent=''):
    ls = []
    compressors = {
        'css': 'css',
        'js': 'js',
        'json': 'css'
    }

    if not isinstance(target, dict):
        makeString = bcolors.BOLD + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.OKBLUE + target + bcolors.ENDC + ' target...'

        # Check to see if target is a subtarget (i.e., 'quizzes.chord_buider'). It will only be dot-separated
        # if explicitly passed as a build target.
        if '.' in target:
            print(makeString)
            ls = getNestedTarget(target.split('.'), json)
        else:
            print(indent + makeString)
            ls = json.get(target)

        # If compressing any of the known extensions then send it directly to its same-named compressor.
        if target in compressors.keys():
            compress(ls, compressors[target], indent)
        elif target == 'clean':
            clean(json.get(target))
        else:
            for subtarget in ls:
                # For nested targets we want to keep indenting.
                buildTarget(subtarget, ls, indent + '****** ')

    # If a dict then we can't recurse any further, compress the targets and we're done (should only be css,
    # js, or json at this point).
    else:
        css = target.get('css')
        if css:
            compress(target.get('css'), 'css', indent)

        js = target.get('js')
        if js:
            compress(target.get('js'), 'js', indent)

        json = target.get('json')
        if json:
            # This isn't a bug, json uses the css compressor.
            compress(target.get('json'), 'css', indent)

def clean(target):
    if not target:
        print(bcolors.FAIL + '[ERROR]:' + bcolors.ENDC + ' Build target does not exist.')
        sys.exit(2)
    else:
        for t in target:
            run = t.get('run')

            if not run:
                print('Error: No "run" command, aborting...')
                sys.exit(2)
            else:
                os.system(run)

    print('****** ' + bcolors.OKGREEN + 'Done' + bcolors.ENDC + '\n')

def compress(target, compressor, indent=''):
    if not indent:
        indent = '****** '

    print(indent + 'Using compressor: ' + bcolors.UNDERLINE + compressor + bcolors.ENDC)

    for t in target:
        src = t.get('src')
        output = t.get('output')
        dest = t.get('dest', '.')
        version = t.get('version', '')
        dependencies = t.get('dependencies', [])
        exclude = t.get('exclude', [])
        name = t.get('name', '')

        if compressor == 'css' or compressor == 'json':
            compressors.css.compress(src, output, dest, version, dependencies, exclude, name)
        elif compressor == 'js':
            compressors.js.compress(src, output, dest, version, dependencies, exclude, name)

    print(indent + bcolors.OKGREEN + 'Done' + bcolors.ENDC + '\n')

def getNestedTarget(keys, ls):
    for key in keys:
        ls = ls.get(key)

    return ls

if __name__ == '__main__':
#    if len(sys.argv) == 1:
#        usage()
#        sys.exit(2)

    main(sys.argv[1:])

