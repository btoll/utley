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
        --silent       Does not print log information to STDOUT (will print ERROR messages).
        --target, -t   Specify build targets (comma-separated).
        --test         Run the `test` build target.
        --verbose, -v  Print build information.
    '''
    print(textwrap.dedent(str))

def main(argv):
    configFile = 'utley.json'
    runAll = False
    silent = False
    target = None
    targets = None
    verbose = False

    if len(argv) == 0:
        runAll = True
    else:
        try:
            opts, args = getopt.getopt(argv, 'hc:t:v', ['help', 'all', 'config=', 'clean', 'lint', 'silent', 'target=', 'test', 'verbose'])
        except getopt.GetoptError:
            print(bcolors.RED + '[ERROR]' + bcolors.ENDC + ' Unrecognized flag.')
            usage()
            sys.exit(1)

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
            elif opt == '--silent':
                silent = True
            elif opt in ('-t', '--target'):
                targets = base_compress.make_list(arg)
            elif opt == '--test':
                target = 'test'
            elif opt in ('-v', '--verbose'):
                verbose = True

    if runAll:
        for t in base_compress.whitelistTargets:
            doWhitelistTarget(t, silent)

        initiateBuild(None, verbose, silent, configFile)
    elif target and target in base_compress.whitelistTargets:
        doWhitelistTarget(target, silent)
    elif not target:
        initiateBuild(targets, verbose, silent, configFile)
    else:
        print(bcolors.RED + '[ERROR]' + bcolors.ENDC + ' No "' + target + '" target has been configured, aborting.')
        sys.exit(1)

def initiateBuild(targets=None, verbose=False, silent=False, configFile='utley.json'):
    json = base_compress.getJson(configFile)

    if targets:
        for target in targets:
            buildTarget(target, json, verbose, silent)
    else:
        for target in json:
            if target in base_compress.whitelistTargets:
                continue

            buildTarget(target, json, verbose, silent)

def buildTarget(target, json, verbose=False, silent=False, indent=''):
    ls = []

    if not isinstance(target, dict):
        makeString = bcolors.BROWN + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.BLUE + target + bcolors.ENDC + ' target...'

        # Check to see if target is a subtarget (i.e., 'quizzes.chord_buider'). It will only be dot-separated
        # if explicitly passed as a build target.
        if '.' in target:
            if not silent:
                print(makeString)

            ls = getNestedTarget(target.split('.'), json)
            for key in target.split('.'):
                ls = ls.get(key)
        else:
            if not silent:
                print(indent + makeString)

            ls = json.get(target)

        # If compressing any of the known extensions then send it directly to its same-named compressor.
        if target in base_compress.compressors.keys():
            compress(ls, target, base_compress.compressors[target], verbose, silent, indent)
        elif target in base_compress.whitelistTargets:
            doWhitelistTarget(target, silent, json.get(target))
        else:
            for subtarget in ls:
                # For nested targets we want to keep indenting.
                buildTarget(subtarget, ls, verbose, silent, indent + '****** ')

    else:
        # If a dict then we can't recurse any further, build the whitelisted targets and we're done.
        for key, value in target.items():
            if key in base_compress.compressors.keys():
                compress(target.get(key), key, base_compress.compressors[key], verbose, silent, indent)
            elif key in base_compress.whitelistTargets:
                doWhitelistTarget(key, silent, target.get(key))

def compress(target, targetName, compressor, verbose=False, silent=False, indent=''):
    if not indent:
        indent = '****** '

    if not silent:
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

    if not silent:
        print(indent + bcolors.GREEN + 'Done' + bcolors.ENDC + '\n')

def doRun(target, silent=False):
    if not target and not silent:
        print(bcolors.YELLOW + '[WARNING]' + bcolors.ENDC + ' Expecting a "run" command but none found.')
    else:
        if subprocess.call(shlex.split(target)) > 0:
            print(bcolors.RED + '[ERROR]' + bcolors.ENDC + ' There has been a problem!')
            sys.exit(1)

def doWhitelistTarget(name, silent=False, target=None, json=base_compress.getJson('utley.json')):
    if not silent:
        print(bcolors.BROWN + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.BLUE + name + bcolors.ENDC + ' target...')

    if not target:
        target = json.get(name)

    # Let's not throw or exit early if a whitelisted target doesn't exist.
    if target:
        for t in target:
            doRun(t.get('run'), silent)

    if not silent:
        print('****** ' + bcolors.GREEN + 'Done' + bcolors.ENDC + '\n')

if __name__ == '__main__':
    main(sys.argv[1:])

