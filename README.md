#### Utley is all of the following things.

+ A dog (he's Top Dog, actually).

+ A Python build tool.

#### What is the license?
+ Utley is [free][wtfpl].

[wtfpl]: http://www.wtfpl.net/

#### Usage

Build all targets (assumes an `utley.json` build file).

    utley

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

Clean (assuming it's defined in the `tasks` block).

    utley --task=clean
    utley --clean

Lint (assuming it's defined in the `tasks` block).

    utley --task=lint
    utley --lint

Test (assuming it's defined in the `tasks` block).

    utley --task=test
    utley --test

Note that any task defined in the `tasks` block can be aliased by:

    utley --[task]

USAGE:

    --config, -c   The location of the build file. Defaults to `utley.json`.
    --silent       Does not print log information to STDOUT (will print ERROR messages).
    --target, -t   Specify build targets (comma-separated).
    --task         Runs the shell command in the `tasks` block.
    --verbose, -v  Print build information.

