Utley is all of the following things.

+ A dog (he's Top Dog, actually).

+ A Python build tool.

What is the license?
+ Utley is [free][wtfpl].

[wtfpl]: http://www.wtfpl.net/

Build all targets (assumes an `utley.json` build file).

    utley
    utley --all

Specify a different build file than the default `utley.json`.

    utley --config=foo.json

Build only the CSS target.

    utley --target=css

Build only the JavaScript target.

    utley --target=js

Build multiple targets.

    utley --target=js,css,quizzes

Build a nested subtarget.

    utley --target=foo.bar.quux

Build whatever you want.

    utley --target=clean,css,quizzes.chord_builder,my_custom_target

Clean.

    utley --clean

Lint.

    utley --lint

Test.

    utley --test

USAGE:

    --all          Run all build targets.
    --clean        Run the `clean` build target.
    --config, -c   The location of the build file. Defaults to `utley.json`.
    --lint         Run the `lint` build target.
    --silent       Does not print log information to STDOUT (will print ERROR messages).
    --target, -t   Specify build targets (comma-separated).
    --test         Run the `test` build target.
    --verbose, -v  Print build information.

