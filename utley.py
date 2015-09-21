# TODO: bake semver into build artifacts.
#
# TODO: spinner!
#        if not silent and not verbose:
#            spinner = itertools.cycle(['-', '\\', '|', '/'])
#
#        if not silent and not verbose:
#            sys.stdout.write(next(spinner))
#            sys.stdout.write('\b')
#            sys.stdout.flush()
#            sys.stdout.write('\b')
#        elif verbose:
#            print(bcolors.ON_BLUE + bcolors.BROWN + '[DEBUG]' + bcolors.ON_WHITE + bcolors.YELLOW + ' Processing -> ' + bcolors.ENDC + script)
#
#        return subprocess.getoutput(compressor + ' ' + src)

import lib.base
from lib.usage import usage
import lib.compressors.css
import fileinput
import lib.message
import getopt
import json
import subprocess
import sys

def main(argv):
    configFile = 'utley.json'
    dumpTarget = None
    silent = False
    task = None
    targets = None
    verbose = False

    if len(argv) == 0:
        # Assumes `utley.json` config file.
        initiateBuild(None, verbose, silent, configFile)
    elif len(argv) == 1 and '--' in argv[0] and not '=' in argv[0]:
        # This provides a shortcut for calling shell commands defined in the `tasks` block. For example, the `clean` script
        # could be called as `utley --clean`. So, anything defined in the `tasks` block can be aliased by prefixing `--`.
        doTask(argv[0][2:], lib.base.getJson(configFile), silent)
    elif len(argv) == 1:
        # This provides a shortcut for calling target. For example, the `build` target could be called as `utley build`.
        initiateBuild(lib.base.make_list(argv[0]), verbose, silent, configFile)
    else:
        try:
            opts, args = getopt.getopt(argv, 'hc:l:v', ['help', 'config=', 'list=', 'silent', 'target=', 'task=', 'verbose'])
        except getopt.GetoptError:
            print(lib.message.error('Unrecognized flag!'))
            usage()
            sys.exit(1)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage()
                sys.exit(0)
            elif opt in ('-c', '--config'):
                configFile = arg
            elif opt in ('-l', '--list'):
                dumpTarget = arg
            elif opt == '--silent':
                silent = True
            elif opt == '--target':
                targets = lib.base.make_list(arg)
            elif opt == '--task':
                task = arg
            elif opt in ('-v', '--verbose'):
                verbose = True

        if dumpTarget:
            print(lib.message.dump_target(dumpTarget))
            print(json.dumps(lib.base.getJson(configFile).get(dumpTarget), indent=4) + '\n')
        elif targets:
            initiateBuild(targets, verbose, silent, configFile)
        elif task:
            doTask(task, lib.base.getJson(configFile), silent)
        else:
            print(lib.message.abort(argv[0]))
            sys.exit(1)

def initiateBuild(targets=None, verbose=False, silent=False, configFile='utley.json'):
    json = lib.base.getJson(configFile)

    if targets:
        for target in targets:
            buildTarget(target, json, verbose, silent)
    else:
        for target in json:
            if target == 'tasks':
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

            ls = json.get(target)

            if containsTargetReferences(ls):
                doTargetReference(ls, json, target, verbose, silent, indent)
            else:
                doTarget(json, target, ls, verbose, silent, indent)

    else:
        # If a dict then we can't recurse any further, compress and we're done.
        for key, value in target.items():
            if key in lib.base.compressors.keys():
                doConcat(target.get(key), key, verbose, silent, indent)

def containsTargetReferences(target):
    return isinstance(target, list) and isinstance(target[0], str)

def doCompress(compressor, targetName, src, verbose=False, silent=False, indent=''):
    if not indent:
        indent = '****** '

    if not silent:
        print(indent + lib.message.compressing(targetName, compressor))

    if targetName == 'css' or targetName == 'json':
        buff = lib.compressors.css.compress(src, verbose, silent)
    elif targetName == 'js':
        buff = subprocess.getoutput(compressor + ' ' + src)

#    if not silent:
#        print(indent + lib.message.end_block())

    return buff

def doConcat(target, targetName, verbose=False, silent=False, indent=''):
    if not indent:
        indent = '****** '

    if not silent:
        print(indent + lib.message.concatting(targetName))

    buff = []

    for t in target:
        src = t.get('src')
        output = t.get('output')
        dependencies = t.get('dependencies', [])
        exclude = t.get('exclude', [])
        name = t.get('name', '')

    ls = lib.base.sift_list(
        lib.base.make_list(src),
        targetName,
        lib.base.make_list(exclude),
        lib.base.make_list(dependencies)
    )

    with fileinput.input(ls) as f:
        for line in f:
            buff.append(line)

    lib.base.write_buffer(buff, output)

    doPreprocessing(targetName, output, verbose=False, silent=False, indent='')

    if not silent:
        print(indent + lib.message.end_block())

#    for script in ls:
#        # If script is a named target then retrieve it from the global `builds` dict.
#        # Note that it assumes the named target was already built!
#        if script[0] == '@':
#            buff.append(''.join(builds.get(script[1:])))
#        else:
#        if name:
#            builds.update({
#                name: buff
#            })
#
#        buff.append(subprocess.getoutput('babel ' + script + ' | java -jar ' + jar + ' --type js'))

def doPreprocessing(targetName, output, verbose=False, silent=False, indent=''):
    manifest = lib.base.getManifest()

    if manifest:
        rc = lib.base.getJson(manifest)
        lang = None
        transpile = None
        compress = None

        if rc:
            buff = []
            lang = rc.get(targetName)

            if lang:
                transpile = lang.get('transpile')
                compress = lang.get('compress')

            if transpile:
                buff = doTranspile(transpile, targetName, output, verbose=False, silent=False)

            if compress:
                buff = doCompress(compress, targetName, output, verbose=False, silent=False)

            lib.base.write_buffer(buff, output)

def doTarget(json, target, ls, verbose, silent, indent):
    # If operating on one of the known extensions then pass it directly on.
    if target in lib.base.compressors.keys():
        doConcat(ls, target, verbose, silent, indent)
    else:
        for subtarget in ls:
            buildTarget(subtarget, ls, verbose, silent,  '****** ')

def doTargetReference(ls, json, target, verbose, silent, indent):
    for ref in ls:
        if ref[0] == '#':
            doTask(ref[1:], json, silent)
        else:
            doTarget(json, ref, json.get(ref), verbose, silent, indent)

def doTask(key, json, silent=False):
    tasks = json.get('tasks')
    task = tasks.get(key)

    if task:
        if not silent:
            print('****** ' + lib.message.open_block(key))

        # Instead of handling a non-zero exit code here and throwing, each shell command will have
        # to clean up after itself.
        subprocess.call(task, shell=True)

        if not silent:
            print('****** ' + lib.message.end_block())
    elif not task and not silent:
        print(lib.message.warning(key))
        sys.exit(1)

def doTranspile(transpiler, target, src, verbose=False, silent=False, indent=''):
    if not indent:
        indent = '****** '

    if not silent:
        print(indent + lib.message.transpiling(target, transpiler))

    return subprocess.getoutput(transpiler + ' ' + src)

#    if not silent:
#        print(indent + lib.message.end_block())

    return buff

def getNestedTarget(keys, ls):
    for key in keys:
        ls = ls.get(key)

    return ls

if __name__ == '__main__':
    main(sys.argv[1:])

