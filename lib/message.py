from lib.bcolors import bcolors

def abort(target):
    return bcolors.RED + '[ERROR]' + bcolors.ENDC + ' No ' + bcolors.PURPLE + target + bcolors.ENDC + ' target found, aborting.'

def compressing(name, compressor):
    return 'Compressing target ' + bcolors.BROWN + name + bcolors.ENDC + ' with compressor: ' + bcolors.UNDERLINE + compressor + bcolors.ENDC

def concatting(name, compressor):
    return 'Concatenating target ' + bcolors.BROWN + name + bcolors.ENDC

def dump_target(target):
    return 'Printing ' + bcolors.BLUE + target + bcolors.ENDC + ' target:\n'

def end_block():
    return '****** ' + bcolors.GREEN + 'Done' + bcolors.ENDC + '\n'

def error(msg):
    return bcolors.RED + '[ERROR]' + bcolors.ENDC + ' ' + msg

def open_block(name):
    return bcolors.BROWN + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.BLUE + name + bcolors.ENDC + ' target...'

def warning(task):
    return bcolors.YELLOW + '[WARNING]' + bcolors.ENDC + ' Unrecognized task ' + bcolors.PURPLE + task + bcolors.ENDC

