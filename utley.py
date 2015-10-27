# TODO: Bake semver into build artifacts.
# TODO: Make more verbose.

import lib.base
from lib.usage import usage
import lib.compressors.css
import getopt
import json
import itertools
import subprocess
import sys

builds = {}

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
        opt = argv[0][2:]

        if opt == 'help':
            usage()
            sys.exit(0)

        doTask(opt, lib.base.getJson(configFile), verbose, silent)

    elif len(argv) == 1 and not '=' in argv[0] and not '-' in argv[0]:
        # This provides a shortcut for calling target. For example, the `build` target could be called as `utley build`.
        initiateBuild(lib.base.make_list(argv[0]), verbose, silent, configFile)
    else:
        try:
            opts, args = getopt.getopt(argv, 'hc:l:v', ['config=', 'list=', 'silent', 'target=', 'task=', 'verbose'])
        except getopt.GetoptError:
            print('[ERROR] Unrecognized flag!')
            usage()
            sys.exit(1)

        for opt, arg in opts:
            if opt == '-h':
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
            print(json.dumps(lib.base.getJson(configFile).get(dumpTarget), indent=4) + '\n')
        elif targets:
            initiateBuild(targets, verbose, silent, configFile)
        elif task:
            doTask(task, lib.base.getJson(configFile), verbose, silent)
        else:
            print('[ERROR] No ' + target + ' target found, aborting.')
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

def buildTarget(target, json, verbose=False, silent=False):
    if not isinstance(target, dict):
        # Check to see if target is a subtarget (i.e., 'quizzes.chord_buider'). It will only be dot-separated
        # if explicitly passed as a build target.
        ls = checkNestedTarget(target, json)

        if not silent:
            print('Initiating ' + target + ' target...')

        if containsTargetReferences(ls):
            doTargetReference(ls, json, target, verbose, silent)
        else:
            doTarget(json, target, ls, verbose, silent)

    else:
        # If a dict then we can't recurse any further, compress and we're done.
        for key, value in target.items():
            if key in lib.base.compressors.keys():
                doConcat(target.get(key), key, verbose, silent)

def checkNestedTarget(target, json):
    if '.' in target:
        ls = getNestedTarget(target.split('.'), json)
    else:
        ls = json.get(target)

    return ls

def containsTargetReferences(target):
    return isinstance(target, list) and isinstance(target[0], str)

def doCompress(compressor, targetName, src, verbose=False, silent=False):
    if not silent:
        message = '[INF] Compressing target ' + targetName

        # Note that the CSS is compressed using regexes so there is no compressor to name.
        if not isinstance(compressor, bool):
            message += ' with compressor ' + compressor

        message += '... '
        spinner(message)

    if targetName == 'css' or targetName == 'json':
        buff = lib.compressors.css.compress(src, verbose, silent)
    elif targetName == 'js':
        buff = subprocess.getoutput(compressor + ' ' + src)

    if not silent:
        print('Completed')

    return buff

def doConcat(target, targetName, verbose=False, silent=False):
    global builds

    preprocessed = None

    for t in target:
        if not silent:
            spinner('[INF] Concatenating target ' + targetName + '... ')

        buff = []

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

        for script in ls:
            # If script is a named target then retrieve it from the global `builds` dict.
            # Note that it assumes the named target was already built!
            if script[0] == '@':
                buff.append(''.join(builds.get(script[1:])))
            else:
                script = open(script, 'r')

                for line in script:
                    buff.append(line)

                script.close()

        lib.base.write_buffer(buff, output)

        if not silent:
            print('Completed')

        # If a named target then skip here, it probably was preprocessed the first time when it was built.
        preprocessed = doPreprocessing(targetName, output, verbose, silent)

        if preprocessed:
            lib.base.write_buffer(preprocessed, output)
            buff = preprocessed

        if name:
            builds.update({
                name: buff
            })

def doPreprocessing(targetName, output, verbose=False, silent=False):
    manifest = lib.base.getManifest()

    if manifest:
        rc = lib.base.getJson(manifest)

        if rc:
            lang = None
            transpile = None
            compress = None
            buff = None
            lang = rc.get(targetName)

            if lang:
                transpile = lang.get('transpile')
                compress = lang.get('compress')

            if transpile:
                buff = doTranspile(transpile, targetName, output, verbose, silent)

            if compress:
                buff = doCompress(compress, targetName, output, verbose, silent)

            return buff

    return None

def doTarget(json, target, ls, verbose, silent):
    # If operating on one of the known extensions then pass it directly on.
    if target in lib.base.compressors.keys():
        doConcat(ls, target, verbose, silent)
    else:
        if ls == None:
            print('[ERROR] Unrecognized target `' + target + '`')
            sys.exit(1)
        else:
            for subtarget in ls:
                buildTarget(subtarget, ls, verbose, silent)

def doTargetReference(ls, json, target, verbose, silent):
    for ref in ls:
        if ref[0] == '#':
            doTask(ref[1:], json, verbose, silent)
        else:
            ls = checkNestedTarget(ref, json)
            doTarget(json, ref, ls, verbose, silent)

def doTask(key, json, verbose=False, silent=False):
    tasks = json.get('tasks')
    task = tasks.get(key)

    if task:
        if verbose:
            print('[DEBUG] Processing -> ' + task)

        if not silent:
            spinner('[INF] Running ' + key + ' target... ')

        # Instead of handling a non-zero exit code here and throwing, each shell command will have
        # to clean up after itself.
        subprocess.call(task, shell=True)

        if not silent:
            print('Completed')
    elif not task and not silent:
        print('[ERROR] Unrecognized task `' + key + '`')
        sys.exit(1)

def doTranspile(transpiler, target, src, verbose=False, silent=False):
    if not silent:
        spinner('[INF] Transpiling target ' + target + ' using ' +  transpiler + '... ')

    buff = subprocess.getoutput(transpiler + ' ' + src)

    if not silent:
        print('Completed')

    return buff

def getNestedTarget(keys, ls):
    for key in keys:
        ls = ls.get(key)

    return ls

def spinner(msg):
    spinner = itertools.cycle(['-', '\\', '|', '/'])

    sys.stdout.write(msg + next(spinner))
    sys.stdout.write('\b')
    sys.stdout.flush()
    sys.stdout.write('\b')

if __name__ == '__main__':
    main(sys.argv[1:])

