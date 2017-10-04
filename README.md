# Color schemes for JOE

This repository contains color schemes for [Joe's Own Editor](https://sf.net/p/joe-editor),
as well as a handful of miscellaneous utilities to generate and convert
color schemes.

## Color schemes

If you're only looking for color schemes, you will find them in the
[custom](https://github.com/jjjordan/joe-colors/tree/master/custom) and
[output](https://github.com/jjjordan/joe-colors/tree/master/output)
directories.  Those in `custom` are hand written, and those in `output` are
generated from VIM schemes found in the `vim-schemes` directory.

## More color schemes

More color schemes are available from the
[base16-joe](https://github.com/jjjordan/base16-joe) repository, which
contains the templates necessary to build JCF files for the color schemes
supported by the [base16 project](https://github.com/chriskempson/base16).

The `create256.py` script in **this** repository will convert the GUI colors
from those output files, and amend xterm-256 sections to each one.  This
script is to be run before checking in JCF files to that repository.

## Converting from VIM schemes

Most of the schemes here are generated from the VIM script schemes, which is
performed by the `convertvim.py` program.  The `Makefile` here is also
geared towards automating this process:

```sh
make -j4 all
```

* This will create the virtualenv for you and install dependencies if not
already done.
* The `all` target is necessary to build all schemes.  The default target,
`prod` only builds those schemes that are included in the default
distribution of JOE.
* You'll want to build with multiple cores (`-j`) for the fastest result. 
Color scheme generation is an expensive operation due to the complications
converting them to xterm-256 (properly) and matching terminal colors.

Additional options are set in `overrides.json`, which specifies things like
attributions, color overrides, and the like.

### VIM syntax

This conversion process only works with a subset of VIM color schemes. 
Since I didn't implement a full VIM parser and runtime, any scheme that
cheats and uses any kind of function will fail to convert.  Only schemes
that use the straightforward `hi`/`highlight`/`hi link` commands will work
correctly.

Many schemes do, however, use branching to check for enabled options -- for
example, to switch between light and dark versions.  I've "amended" the
syntax to add `do` and `dont`, indicating which branches should be taken or
skipped.  The parser will properly match if's and else's beyond that.
