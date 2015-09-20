import json
import os
import re
import sys

compressors = {
    'css': 'css',
    'js': 'js',
    'json': 'css'
}

def filter_exclusions(root, exclude=[], suffix='js'):
    # Any element in the exclude list is assumed to have an absolute path to the source directory.
    matches = []

    # Normalize by making any path entry in the exclude list absolute.
    exclude = make_abspath(root, exclude)

    for dirpath, dirnames, filenames in os.walk(root):
        # First add all filenames to the list.
        #
        # Note we compare the joined dirpath/f against the elements in the exclude list. They will both
        # reference the same source location.
        matches += [os.path.join(dirpath, f) for f in filenames if re.search('.' + suffix + '$', f) and os.path.join(dirpath, f) not in exclude]

        # Then remove any dirnames in our exclude list so any filenames contained
        # within them are not included.
        #
        # Note here we have to compare the function arg `root` against the exclude list.
        [dirnames.remove(d) for d in dirnames if os.path.join(root, d) in exclude]

    return matches

def getJson(resource='utley.json'):
    try:
        # TODO: Is there a better way to get the values from the Json?
        with open(resource, mode='r', encoding='utf-8') as f:
            jsonData = json.loads(f.read())

        return jsonData

    # Exceptions could be bad Json or file not found.
    except (ValueError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)

def make_abspath(root, ls):
    return [os.path.join(root, f) for f in ls]

def make_list(ls):
    # Split string by comma and strip leading and trailing whitepace from each list element.
    return ls if type(ls) is list else [f.strip() for f in ls.split(',')]

def process_files(src, files):
    return [f for f in make_abspath(src, files) if os.path.isfile(f)]

def sift_list(root, suffix, exclude=[], dependencies=[]):
    # TODO: add more line comments!
    # Clone.
    original = dependencies[:]
    target = []

    # `root` should always be a list.
    for src in root:
        # If the src is a name, i.e., it refers to a previous build target, just add it to the target list and continue.
        if src[0] == '@':
            target += [src]
            continue

        if os.path.isfile(src):
            target += [src]
        else:
            # Let's only operate on filenames with absolute paths.
            dependencies = process_files(src, original)
            matches = filter_exclusions(src, exclude, suffix)

            # Make sure our dependencies are at the front of the stack and not duped. The
            # new list will be the target list of files to be processed by the minifier.
            target += (dependencies + [f for f in matches if f not in dependencies])

        if (len(target) <= 0):
            print('OPERATION ABORTED: Either no ' + suffix.upper() + ' source files were found in the specified source directory or there were more exclusions than source files.')
            sys.exit(1)

    return target

def write_buffer(buff, output):
    if '/' in output:
        dest, output = os.path.split(output)

    # This will overwrite pre-existing.
    if dest != '.':
        os.makedirs(dest, exist_ok=True)

    with open(dest + '/' + output, mode='w', encoding='utf-8') as fp:
        # Flush the buffer (only perform I/O once).
        fp.write(''.join(buff))

