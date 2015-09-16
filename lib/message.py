from lib.bcolors import bcolors

def abort(name):
    return bcolors.RED + '[ERROR]' + bcolors.ENDC + ' No "' + name + '" target has been configured, aborting.'

def building_target(name, compressor):
    return 'Building target ' + bcolors.BROWN + name + bcolors.ENDC + ' with compressor: ' + bcolors.UNDERLINE + compressor + bcolors.ENDC

def end_block():
    return '****** ' + bcolors.GREEN + 'Done' + bcolors.ENDC + '\n'

def error(msg):
    return bcolors.RED + '[ERROR]' + bcolors.ENDC + ' ' + msg

def open_block(name):
    return bcolors.BROWN + '[INF]' + bcolors.ENDC + '  Making ' + bcolors.BLUE + name + bcolors.ENDC + ' target...'

def warning():
    return bcolors.YELLOW + '[WARNING]' + bcolors.ENDC + ' Expecting a shell command but none found.'

