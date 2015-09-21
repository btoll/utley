from lib.bcolors import bcolors

def abort(target):
    return bcolors.RED + '[ERROR]' + bcolors.ENDC + ' No ' + bcolors.PURPLE + target + bcolors.ENDC + ' target found, aborting.'

def compressing(name, compressor):
    message = 'Compressing target ' + bcolors.BROWN + name + bcolors.ENDC

    # Note that the CSS is compressed using regexes so there is no compressor to name.
    if not isinstance(compressor, bool):
        message += ' with compressor ' + bcolors.BROWN + compressor + bcolors.ENDC

    return message

def concatting(name):
    return 'Concatenating target ' + bcolors.BROWN + name + bcolors.ENDC

def dump_target(target):
    return 'Printing ' + bcolors.BLUE + target + bcolors.ENDC + ' target:\n'

def end_block():
    return '****** ' + bcolors.GREEN + 'Done' + bcolors.ENDC + '\n'

def error(msg):
    return bcolors.RED + '[ERROR]' + bcolors.ENDC + ' ' + msg

def open_block(name):
    return bcolors.BROWN + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.BLUE + name + bcolors.ENDC + ' target...'

def transpiling(name, transpiler):
    return 'Transpiling target ' + bcolors.BROWN + name + bcolors.ENDC + ' using ' + bcolors.BROWN + transpiler + bcolors.ENDC

def warning(task):
    return bcolors.YELLOW + '[WARNING]' + bcolors.ENDC + ' Unrecognized task ' + bcolors.PURPLE + task + bcolors.ENDC

