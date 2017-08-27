# dotlink

A python script to create symlinks in the home directory pointing to your
dotfiles.

## dotpends

dotlink supports system specific dotfiles through the use of *dotpends*.

*dotpends* are dotfiles prefixed with a system name, for example:

    osx.profile
    win.profile

Preferably, *dotpends* should live in a sub-directory of your dotfiles
directory. Link *dotpends* with `dotlink.py -p <system name>`.

## Manifest

After each run, dotlink will create (or overwrite) a manifest file in your home
directory called `.dotlink`. This is a csv file containing one row for each
dotfile or dotpends found, with the format:

    source_location,link_location

The manifest should not include any blank lines.

## Extra

Add `dotlink.py` to your path:

    git clone https://github.com/bmweiner/dotlink.git
    cd dotlink
    chmod +x dotlink.py
    ln dotlink.py /usr/bin/dotlink.py

## Examples

Given the following dotfiles directory structure:

    ~/dotfiles
    ├── .bash_profile
    ├── .bashrc
    ├── .gitconfig
    ├── .gitignore
    ├── .inputrc
    ├── .minttyrc
    ├── .octaverc
    ├── .pypirc
    ├── .vim
    │   ├── autoload
    │   │   └── pathogen.vim
    │   └── bundle
    │       └── plugin
    │           └── sensible.vim
    ├── .vimrc
    ├── README.md
    ├── dotlink.py
    ├── dotpends
    │   ├── osx.profile
    │   └── win.profile
    └── scripts
        └── Markdown.pl

linking only the dotfiles:

    cd ~/dotfiles
    ./dotlink.py

linking both dotfiles and dotpends for a system named osx:

    ./dotlink.py -p osx

passing a dotfiles directory manually:

    ./dotlink.py ~/dotfiles

passing a dotpends directory manually:

    ./dotlink.py -p osx -dp ~/dotfiles/dotpends

overwriting existing symlinks (note: `-f` will only overwrite symlinks, actual
files or folders must be removed manually):

    ./dotlink.py -f

excluding dotfiles (note: certain files are always excluded (ex: .git)):

    ./dotlink -e .bash_profile .bashrc

manually specifying the links to create with a manifest:

    ./dotlink -m ~/.dotlink

## Dependencies

 * Python 2 or Python 3
 * Tested on OSX and Windows (must run as administrator)
