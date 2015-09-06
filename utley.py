# TODO: accessors for get/set configFile!
import lib.base
from lib.usage import usage
import lib.compressors.css
import lib.compressors.js
import lib.message
import getopt
import shlex
import subprocess
import sys

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
            print(lib.message.error('Unrecognized flag!'))
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
                targets = lib.base.make_list(arg)
            elif opt == '--test':
                target = 'test'
            elif opt in ('-v', '--verbose'):
                verbose = True

    if runAll:
        for t in lib.base.whitelistTargets:
            doWhitelistTarget(t, silent)

        initiateBuild(None, verbose, silent, configFile)
    elif target and target in lib.base.whitelistTargets:
        doWhitelistTarget(target, silent)
    elif not target:
        initiateBuild(targets, verbose, silent, configFile)
    else:
        print(lib.message.abort(target))
        sys.exit(1)

def initiateBuild(targets=None, verbose=False, silent=False, configFile='utley.json'):
    json = lib.base.getJson(configFile)

    if targets:
        for target in targets:
            buildTarget(target, json, verbose, silent)
    else:
        for target in json:
            if target in lib.base.whitelistTargets:
                continue

            buildTarget(target, json, verbose, silent)

def buildTarget(target, json, verbose=False, silent=False, indent=''):
    ls = []

    if not isinstance(target, dict):
        # Check to see if target is a subtarget (i.e., 'quizzes.chord_buider'). It will only be dot-separated
        # if explicitly passed as a build target.
        if '.' in target:
            if not silent:
                print(lib.message.open_block(target))

            ls = getNestedTarget(target.split('.'), json)
        else:
            if not silent:
                print(indent + lib.message.open_block(target))

            if isTargetReference(target):
                target = target[1:]

            ls = json.get(target)

        doTarget(json, target, ls, verbose, silent, indent)

    else:
        # If a dict then we can't recurse any further, build the whitelisted targets and we're done.
        for key, value in target.items():
            if key in lib.base.compressors.keys():
                compress(target.get(key), key, lib.base.compressors[key], verbose, silent, indent)
            elif key in lib.base.whitelistTargets:
                doWhitelistTarget(key, silent, target.get(key))

def compress(target, targetName, compressor, verbose=False, silent=False, indent=''):
    if not indent:
        indent = '****** '

    if not silent:
        print(indent + lib.message.building_target(targetName, compressor))

    for t in target:
        src = t.get('src')
        output = t.get('output')
        dest = t.get('dest', '.')
        version = t.get('version', '')
        dependencies = t.get('dependencies', [])
        exclude = t.get('exclude', [])
        name = t.get('name', '')

        if compressor == 'css' or compressor == 'json':
            lib.compressors.css.compress(src, output, dest, version, dependencies, exclude, name, verbose)
        elif compressor == 'js':
            lib.compressors.js.compress(src, output, dest, version, dependencies, exclude, name, verbose)

    if not silent:
        print(indent + lib.message.end_block())

def doRun(target, silent=False):
    if not target and not silent:
        print(lib.message.warning())
    else:
        if subprocess.call(shlex.split(target)) > 0:
            print(lib.message.error('There has been a problem!'))
            sys.exit(1)

def doTarget(json, target, ls, verbose, silent, indent):
    # If compressing any of the known extensions then send it directly to its same-named compressor.
    if target in lib.base.compressors.keys():
        compress(ls, target, lib.base.compressors[target], verbose, silent, indent)
    elif target in lib.base.whitelistTargets:
        doWhitelistTarget(target, silent, json.get(target))
    else:
        if not ls:
            ls = json

        for subtarget in ls:
            # For nested targets we want to keep indenting.
            if isTargetReference(subtarget):
                subtarget = subtarget[1:]
                ls = json
            else:
                indent += '****** '

            buildTarget(subtarget, ls, verbose, silent, indent)

def doWhitelistTarget(name, silent=False, target=None, json=lib.base.getJson('utley.json')):
    if not silent:
        print(lib.message.open_block(name))

    if not target:
        target = json.get(name)

    # Let's not throw or exit early if a whitelisted target doesn't exist.
    if target:
        for t in target:
            doRun(t.get('run'), silent)

    if not silent:
        print('****** ' + lib.message.end_block())

def getNestedTarget(keys, ls):
    for key in keys:
        ls = ls.get(key)

    return ls

def isTargetReference(target):
    return isinstance(target, str) and target[0] == '#'

if __name__ == '__main__':
    main(sys.argv[1:])

