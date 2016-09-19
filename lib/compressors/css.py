import lib.base
import re
import sys

def compress(src, verbose=False, silent=False, jar=None):
    if not src:
        print('Error: No source, nothing to do!')
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
            print('[DEBUG] Processing -> ' + outputFile)

        src = reStripComments.sub('', src)
        src = reRemoveWhitespace.sub(replace_match, src)
        src = reTrim.sub('', src)
        src = reReplaceDoubleSpaces.sub(' ', src)

        return src

    except (KeyboardInterrupt, EOFError):
        # Control-C or Control-D sent a SIGINT to the process, handle it.
        print('\nProcess aborted!')
        sys.exit(1)

def replace_match(match_obj):
    if not match_obj.group(1) == '':
        return match_obj.group(1)
    else:
        return ''

