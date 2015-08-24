# TODO: Add global var for visual spacing '******'
# TODO: accessors for get/set configFile!
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
        utley --all
        # Note that the above are synonyms.

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

        # Lint.
        utley --lint

        # Test.
        utley --test

        --all          Run all build targets.
        --clean        Run the `clean` build target.
        --config, -c   The location of the build file. Defaults to `utley.json`.
        --lint         Run the `lint` build target.
        --target, -t   Specify build targets (comma-separated).
        --test         Run the `test` build target.
        --verbose, -v  Print build information.
    '''
    print(textwrap.dedent(str))

def main(argv):
    configFile = 'utley.json'
    runAll = False
    target = None
    targets = None
    verbose = False

    if len(argv) == 0:
        runAll = True
    else:
        try:
            opts, args = getopt.getopt(argv, 'hc:t:v', ['help', 'all', 'config=', 'clean', 'lint', 'target=', 'test', 'verbose'])
        except getopt.GetoptError:
            print('Error: Unrecognized flag.')
            usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
                sys.exit(0)
            elif opt == '--all':
                runAll = True
            elif opt in ('-c', '--config'):
                configFile = arg
            elif opt == '--clean':
                target = 'clean'
            elif opt == '--lint':
                target = 'lint'
            elif opt in ('-t', '--target'):
                targets = base_compress.make_list(arg)
            elif opt == '--test':
                target = 'test'
            elif opt in ('-v', '--verbose'):
                verbose = True

    if runAll:
        for t in base_compress.whitelistTargets:
            doWhitelistTarget(t)

        initiateBuild(None, verbose, configFile)
    elif target and target in base_compress.whitelistTargets:
        doWhitelistTarget(target)
    elif not target:
        initiateBuild(targets, verbose, configFile)
    else:
        print(bcolors.RED + '[ERROR]' + bcolors.ENDC + ' No "' + target + '" target has been configured, aborting.')

def initiateBuild(targets=None, verbose=False, configFile='utley.json'):
    json = base_compress.getJson(configFile)

    if targets:
        for target in targets:
            buildTarget(target, json, verbose)
    else:
        for target in json:
            if target in base_compress.whitelistTargets:
                continue

            buildTarget(target, json, verbose)

def buildTarget(target, json, verbose, indent=''):
    ls = []

    if not isinstance(target, dict):
        makeString = bcolors.BROWN + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.BLUE + target + bcolors.ENDC + ' target...'

        # Check to see if target is a subtarget (i.e., 'quizzes.chord_buider'). It will only be dot-separated
        # if explicitly passed as a build target.
        if '.' in target:
            print(makeString)

            ls = getNestedTarget(target.split('.'), json)
            for key in target.split('.'):
                ls = ls.get(key)
        else:
            print(indent + makeString)
            ls = json.get(target)

        # If compressing any of the known extensions then send it directly to its same-named compressor.
        if target in base_compress.compressors.keys():
            compress(ls, target, base_compress.compressors[target], verbose, indent)
        elif target in base_compress.whitelistTargets:
            doWhitelistTarget(target, json.get(target))
        else:
            for subtarget in ls:
                # For nested targets we want to keep indenting.
                buildTarget(subtarget, ls, verbose, indent + '****** ')

    else:
        # If a dict then we can't recurse any further, build the whitelisted targets and we're done.
        for key, value in target.items():
            if key in base_compress.compressors.keys():
                compress(target.get(key), key, base_compress.compressors[key], verbose, indent)
            elif key in base_compress.whitelistTargets:
                doWhitelistTarget(key, target.get(key))

def compress(target, targetName, compressor, verbose, indent=''):
    if not indent:
        indent = '****** '

    print(indent + 'Building target ' + bcolors.BROWN + targetName + bcolors.ENDC + ' with compressor: ' + bcolors.UNDERLINE + compressor + bcolors.ENDC)

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

    print(indent + bcolors.GREEN + 'Done' + bcolors.ENDC + '\n')

def doRun(target):
    if not target:
        print(bcolors.YELLOW + '[WARNING]' + bcolors.ENDC + ' Expecting a "run" command but none found.')
    else:
        subprocess.call(shlex.split(target))

def doWhitelistTarget(name, target=None, json=base_compress.getJson('utley.json')):
    print(bcolors.BROWN + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.BLUE + name + bcolors.ENDC + ' target...')

    if not target:
        target = json.get(name)

    # Let's not throw or exit early if a whitelisted target doesn't exist.
    if target:
        for t in target:
            doRun(t.get('run'))

    print('****** ' + bcolors.GREEN + 'Done' + bcolors.ENDC + '\n')

if __name__ == '__main__':
    main(sys.argv[1:])

