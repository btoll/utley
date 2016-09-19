import textwrap

def usage():
    str = '''
        USAGE:

        # Build all targets (assumes an `utley.json` build file).
        utley

        # Specify a different build file than the default `utley.json`.
        utley -c foo.json
        # Build only the CSS target.
        utley css

        # Build only the JavaScript target.
        utley js

        # Build multiple targets.
        utley js css quizzes

        # Build a nested subtarget.
        utley foo.bar.quux

        # Build whatever you want.
        utley clean css quizzes.chord_builder my_custom_target

        # Clean
        utley --clean

        # Lint
        utley --lint

        # Test
        utley --test

        List the `js` target.
        utley -l js

        -c         The location of the build file. Defaults to `utley.json`.
        -l         Dump a target to STDOUT.
        -s         Does not print log information to STDOUT (will print ERROR messages).
        --{task}   Runs the shell command in the `tasks` block.
        -v         Print build information.
    '''
    print(textwrap.dedent(str))

