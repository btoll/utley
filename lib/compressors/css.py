import lib.base
from lib.bcolors import bcolors
import re
import sys

def compress(src, output='min.css', dest='.', version='', dependencies=[], exclude=[], name='', verbose=False):
    if not src:
        print('Error: You must provide the location of the source files.')
        sys.exit(1)

    try:
        buff = []
        ls = lib.base.sift_list(
            lib.base.make_list(src),
            'css',
            lib.base.make_list(exclude),
            lib.base.make_list(dependencies)
        )

        def replace_match(match_obj):
            if not match_obj.group(1) == '':
                return match_obj.group(1)
            else:
                return ''

        # Strip out any comments of the "/* ... */" type (non-greedy). The subexpression
        # matches all chars AND whitespace.
        reStripComments = re.compile(r'/\*(?:.|\s)*?\*/')

        # Remove all whitespace before and after the following chars: { } : ; = , < >
        reRemoveWhitespace = re.compile(r'\s*({|}|:|;|=|,|<|>)\s*')

        # Trim.
        reTrim = re.compile(r'^\s+|\s+$')

        # Lastly, replace all double spaces with a single space.
        reReplaceDoubleSpaces = re.compile(r'\s{2,}')

        for script in ls:
            if verbose:
                print(lib.bcolors.ON_BLUE + lib.bcolors.BROWN + '[DEBUG]' + lib.bcolors.ON_WHITE +  lib.bcolors.YELLOW + ' Processing -> ' + lib.bcolors.ENDC + script)

            # Note that `script` is the full path name.
            with open(script) as f:
                file_contents = f.read()

            file_contents = reStripComments.sub('', file_contents)
            file_contents = reRemoveWhitespace.sub(replace_match, file_contents)
            file_contents = reTrim.sub('', file_contents)
            file_contents = reReplaceDoubleSpaces.sub(' ', file_contents)

            buff.append(file_contents)

        lib.base.write_buffer(buff, output)

    except (KeyboardInterrupt, EOFError):
        # Control-C or Control-D sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

