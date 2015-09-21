import lib.base
from lib.bcolors import bcolors
import re
import sys

def compress(src, verbose=False, silent=False, jar=None):
    if not src:
        print('Error: You must provide the location of the source files.')
        sys.exit(1)

    try:
        # Strip out any comments of the "/* ... */" type (non-greedy). The subexpression
        # matches all chars AND whitespace.
        reStripComments = re.compile(r'/\*(?:.|\s)*?\*/')

        # Remove all whitespace before and after the following chars: { } : ; = , < >
        reRemoveWhitespace = re.compile(r'\s*({|}|:|;|=|,|<|>)\s*')

        # Trim.
        reTrim = re.compile(r'^\s+|\s+$')

        # Lastly, replace all double spaces with a single space.
        reReplaceDoubleSpaces = re.compile(r'\s{2,}')

        if verbose:
            print(bcolors.ON_BLUE + bcolors.BROWN + '[DEBUG]' + bcolors.ON_WHITE +  bcolors.YELLOW + ' Processing -> ' + bcolors.ENDC + src)

        # Note that `src` is the full path name.
        with open(src) as f:
            file_contents = f.read()

        file_contents = reStripComments.sub('', file_contents)
        file_contents = reRemoveWhitespace.sub(replace_match, file_contents)
        file_contents = reTrim.sub('', file_contents)
        file_contents = reReplaceDoubleSpaces.sub(' ', file_contents)

        return file_contents

    except (KeyboardInterrupt, EOFError):
        # Control-C or Control-D sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

def replace_match(match_obj):
    if not match_obj.group(1) == '':
        return match_obj.group(1)
    else:
        return ''

