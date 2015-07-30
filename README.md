Build all targets (assumes an `utley.json` build file).

    utley

Specify a different build file than the default `utley.json`.

    utley --config=foo.json

Build only the CSS target.

    utley --target=css

Build only the JavaScript target.

    utley --target=js

Specify multiple targets.

    utley --target=js,css,quizzes

Build a nested subtarget.

    utley --target=quizzes.chord_builder

Build whatever you want.

    utley --target=js,css,quizzes.chord_builder,json

Clean.

    utley --clean

USAGE:

    --clean       Run the `clean` build target.
    --config, -c  The location of the build file. Defaults to 'utley.json'.
    --target, -t  Specify build targets (comma-separated)

