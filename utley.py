# TODO: Add global var for visual spacing '******'
import base_compress
from bcolors import bcolors
import compressors.css
import compressors.js
import getopt
import os
import shlex
import subprocess
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

        --clean        Run the `clean` build target.
        --config, -c   The location of the build file. Defaults to 'utley.json'.
        --target, -t   Specify build targets (comma-separated).
        --verbose, -v  Print build information.
    '''
    print(textwrap.dedent(str))

def main(argv):
    clean = False
    configFile = 'utley.json'
    targets = None
    verbose = False

    # If there are no given arguments, assume an utley.json file and both build targets.
    if len(argv) == 0:
        json = base_compress.getJson()
    else:
        try:
            opts, args = getopt.getopt(argv, 'hc:t:v', ['help', 'config=', 'clean', 'target=', 'verbose'])
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
                clean = True
            elif opt in ('-t', '--target'):
                targets = base_compress.make_list(arg)
            elif opt in ('-v', '--verbose'):
                verbose = True

        json = base_compress.getJson(configFile)

    if not clean:
        build(json, targets, verbose)
    else:
        print(bcolors.BOLD + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.OKBLUE + 'clean' + bcolors.ENDC + ' target...')

        doClean(json.get('clean'))

def build(json={}, targets=None, verbose=False):
    skipTargets = [
        'clean',
        'run'
    ]

    if targets:
        for target in targets:
            buildTarget(target, json, verbose)
    else:
        # We're building all targets.

        cleanTarget = json.get('clean')
        if cleanTarget:
            print(bcolors.BOLD + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.OKBLUE + 'clean' + bcolors.ENDC + ' target...')

            doClean(cleanTarget)

        runTarget = json.get('run')
        if runTarget:
            doRun(runTarget)

        for target in json:
            # Skip the clean target!
            if target in skipTargets:
                continue

            buildTarget(target, json, verbose)

def buildTarget(target, json, verbose, indent=''):
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
            compress(ls, compressors[target], verbose, indent)
        elif target == 'clean':
            doClean(json.get(target))
        else:
            for subtarget in ls:
                # For nested targets we want to keep indenting.
                buildTarget(subtarget, ls, verbose, indent + '****** ')

    # If a dict then we can't recurse any further, compress the targets and we're done (should only be css,
    # js, or json at this point).
    else:
        runTarget = target.get('run')
        if runTarget:
            subprocess.call(shlex.split(runTarget))

        css = target.get('css')
        if css:
            compress(target.get('css'), 'css', verbose, indent)

        js = target.get('js')
        if js:
            compress(target.get('js'), 'js', verbose, indent)

        json = target.get('json')
        if json:
            # This isn't a bug, json uses the css compressor.
            compress(target.get('json'), 'css', verbose, indent)

def compress(target, compressor, verbose, indent=''):
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
            compressors.css.compress(src, output, dest, version, dependencies, exclude, name, verbose)
        elif compressor == 'js':
            compressors.js.compress(src, output, dest, version, dependencies, exclude, name, verbose)

    print(indent + bcolors.OKGREEN + 'Done' + bcolors.ENDC + '\n')

def doClean(target):
    if not target:
        print(bcolors.FAIL + '[ERROR]' + bcolors.ENDC + ' Build target does not exist.')
        sys.exit(2)
    else:
        for t in target:
            doRun(t.get('run'))

    print('****** ' + bcolors.OKGREEN + 'Done' + bcolors.ENDC + '\n')

def doRun(target):
    if not target:
        print(bcolors.FAIL + '[ERROR]' + bcolors.ENDC + ' No "run" command, aborting.')
        sys.exit(2)
    else:
        subprocess.call(shlex.split(target))

def getNestedTarget(keys, ls):
    for key in keys:
        ls = ls.get(key)

    return ls

if __name__ == '__main__':
    main(sys.argv[1:])

