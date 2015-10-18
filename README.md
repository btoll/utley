# Utley is all of the following things:

+ A dog (he's Top Dog, actually).

+ A second baseman.

+ A Python build tool.

## The Big Idea

All targets are only concerned with minifying and/or uglifying `JavaScript`, `CSS` and `JSON`.  So, whether top-level or nested, all targets should be an array consisting of one or more objects with the following properties:

    Property | Description
    ------------ | -------------
    src | The location of the source file or directory to be processed.
    output | The location where the build artifact will be written. Note it will create any directories it needs and overwrite any existing file(s).
    dependencies | This allows one to specify the order with which the files should be processed. Obviously, any file in this list will not be processed twice. (optional)
    exclude | Any files that should be ignored. (optional)
    name | Allows the target to have a name that later targets can reference. This is an optimization, as later targets can use the cached build artifact. (optional)

If nested, the tool will recurse until it finds one or more of the aforementioned technologies, which are considered the recursion's terminal case.

For example, the following targets are top-level objects:

    "css": [{
        "src": [
            "../PeteJS/resources/css/",
            "resources/css/"
        ],
        "output": "build/music_theory.css"
    }, {
        "src": "app/quizzes/chord_builder/",
        "output": "build/quizzes/chord_builder/quiz.css"
    }, {
        "src": "app/quizzes/key_signature/",
        "output": "build/quizzes/key_signature/quiz.css"
    }],

    "js": [{
        "name": "Pete",
        "src": "../PeteJS/src/",
        "output": "build/pete.js",
        "dependencies": [
            "Pete.prototype.js",
            "Pete.js",
            "Pete.Observer.js",
            "Pete.Element.js",
            "Pete.Composite.js"
        ]
    }, {
        "src": [
            "@Pete",
            "app/app.js"
        ],
        "output": "build/music_theory.js"
    }],

    "json": [{
        "src": "app.json",
        "output": "build/app.json"
    }],

    ...

(Note the reference to the `@Pete` target name. This allows the `build/music_theory.js` artifact to reference the cached `build/pete.js` artifact, which in this case is going to concatenate `app/app.js` to it.)

These can be called like:

    utley js
    utley css
    utley json
    utley js,css,json

Further, the targets can be nested objects:

    "quizzes": {
        "chord_puzzle": [{
            "css": [{
                "src": "app/quizzes/chord_puzzle/",
                "output": "build/quizzes/chord_puzzle/quiz.css"
            }],

            "js": [{
                "src": "app/quizzes/chord_puzzle/",
                "output": "build/quizzes/chord_puzzle/quiz.js"
            }],

            "json": [{
                "src": "app/chords/sevenths/basic.json",
                "output": "build/chords/sevenths/basic.json"
            }, {
                "src": "app/chords/sevenths/advanced.json",
                "output": "build/chords/sevenths/advanced.json"
            }]
        }],

        "chord_builder": [{
            "css": [{
                "src": "app/quizzes/chord_builder/",
                "output": "build/quizzes/chord_builder/quiz.css"
            }],

            "js": [{
                "src": "app/quizzes/chord_builder/",
                "output": "build/quizzes/chord_builder/quiz.js"
            }]
        }],

        ...

These can be called like:

    utley quizzes
    utley quizzes.chord_puzzle
    utley quizzes.chord_builder

Again, as long as the base cases are `js`, `css` and/or `json`, everything will Just Work.

For everything else, you can specify a task.  This is analogous to npm's `scripts` block.

    "tasks": {
        "clean": "rm -rf build",
        "lint": "eslint app"
    }

These can be called like:

    utley --clean
    utley --lint

Lastly, you can specify other custom build targets that "kick off" other targets and tasks. Note that the tasks must be prefixed by a hash (#).

    "build": [
        "#clean",
        "#lint",
        "css",
        "js",
        "json",
        "quizzes.key_signature"
    ]

As you probably guessed by now, this can be called like:

    utley build

The previous snippets were taken from the `utley.json` [build file] in my [Music Theory][repo] repo.

## CLI Examples

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

## Some `utley.json` Examples In The Wild

+ [build file][build file0] in [benjamintoll.com][repo0] repo.
+ [build file][build file1] in [Music Theory][repo1] repo.
+ [build file][build file2] in [notefile][repo2] repo.
+ [build file][build file3] in [PeteJS][repo3] repo.

## Usage

    Property | Description
    ------------ | -------------
    --config, -c | The location of the build file. Defaults to `utley.json`.
    --help, -h | Help.
    --list, -l | Dump a target to STDOUT.
    --silent | Does not print log information to STDOUT (will print ERROR messages).
    --target | Specify build targets (comma-separated).
    --task | Runs the shell command in the `tasks` block.
    --verbose, -v | Print build information.

## What is the license?
+ Utley is [free][wtfpl].

[build file]: https://github.com/btoll/music_theory/blob/master/utley.json
[repo]: https://github.com/btoll/music_theory
[build file0]: https://github.com/btoll/benjamintoll.com/blob/master/utley.json
[build file1]: https://github.com/btoll/music_theory/blob/master/utley.json
[build file2]: https://github.com/btoll/notefile/blob/master/utley.json
[build file3]: https://github.com/btoll/PeteJS/blob/master/utley.json
[repo0]: https://github.com/btoll/benjamintoll.com
[repo1]: https://github.com/btoll/music_theory
[repo2]: https://github.com/btoll/notefile
[repo3]: https://github.com/btoll/PeteJS
[wtfpl]: http://www.wtfpl.net/

