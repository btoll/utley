# Utley is all of the following things.

+ A dog (he's Top Dog, actually).

+ A second baseman.

+ A Python build tool.

## Examples

##### Targets

*** Note that any target(s) can use the shortcut ***

    utley [target(,s)]

Build only the CSS target.

    utley --target=css
    utley css

Build only the JavaScript target.

    utley --target=js
    utley js

Build multiple targets.

    utley --target=js,css,quizzes
    utley js,css,quizzes

Build a nested subtarget.

    utley --target=foo.bar.quux
    utley foo.bar.quux

Build whatever you want.

    utley --target=clean,css,quizzes.chord_builder,my_custom_target
    utley clean,css,quizzes.chord_builder,my_custom_target

##### Tasks

*** Note that any task defined in the `tasks` block can be aliased by ***

    utley --[task]

Clean (assuming it's defined in the `tasks` block).

    utley --task=clean
    utley --clean

Lint (assuming it's defined in the `tasks` block).

    utley --task=lint
    utley --lint

Test (assuming it's defined in the `tasks` block).

    utley --task=test
    utley --test

##### Other

Build all targets (assumes an `utley.json` build file).

    utley

Specify a different build file than the default `utley.json`.

    utley --config=foo.json

List the `build` target.

    utley --list=build

## utley.json

    {
        "css": [{
            "src": "resources/css",
            "output": "build/main.css"
        }],

        "js": [{
            "src": "lib",
            "output": "build/main.js"
        }],

        "build": [
            "#clean",
            "#lint",
            "css",
            "js"
        ],

        "tasks": {
            "clean": "rm -rf build",
            "lint": "eslint lib"
        }
    }

## Usage

    --config, -c   The location of the build file. Defaults to `utley.json`.
    --help, -h     Help.
    --list, -l     Dump a target to STDOUT.
    --silent       Does not print log information to STDOUT (will print ERROR messages).
    --target       Specify build targets (comma-separated).
    --task         Runs the shell command in the `tasks` block.
    --verbose, -v  Print build information.

## What is the license?
+ Utley is [free][wtfpl].

[wtfpl]: http://www.wtfpl.net/

