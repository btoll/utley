import textwrap

def usage():
    str = '''
        USAGE:

        # Build all targets (assumes an `utley.json` build file).
        utley

        # Specify a different build file than the default `utley.json`.
        utley --config=foo.json
        # Build only the CSS target.
        utley --target=css

        # Build only the JavaScript target.
        utley --target=js

        # Build multiple targets.
        utley --target=js,css,quizzes

        # Build a nested subtarget.
        utley --target=foo.bar.quux

        # Build whatever you want.
        utley --target=clean,css,quizzes.chord_builder,my_custom_target

        # Clean (assuming it's defined in the `tasks` block).
        utley --task=clean
        utley --clean

        # Lint (assuming it's defined in the `tasks` block).
        utley --task=lint
        utley --lint

        # Test (assuming it's defined in the `tasks` block).
        utley --task=test
        utley --test

        Note that any task defined in the `tasks` block can be aliased by:
        utley --[task]

        List the `build` target.
        utley --list=build

        --config, -c   The location of the build file. Defaults to `utley.json`.
        --list, -l     Dump a target to STDOUT.
        --silent       Does not print log information to STDOUT (will print ERROR messages).
        --target, -t   Specify build targets (comma-separated).
        --task         Runs the shell command in the `tasks` block.
        --verbose, -v  Print build information.
    '''
    print(textwrap.dedent(str))

