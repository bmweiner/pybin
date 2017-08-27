import sys
import os
import argparse
import csv

# check platform
win = False
if sys.platform.startswith('win') or sys.platform.startswith('cygwin'):
    import win32file
    import pywintypes
    win = True

def path_error(val):
    """Print path error and raise system exit."""
    print('Invalid path: {}\nTry dotlink.py -h'.format(val))
    raise SystemExit()

def mline(name, source_dir, link_dir, pfx=None):
    """Build manifest line."""
    p_join = os.path.join
    if pfx:
        return [p_join(source_dir, name), p_join(link_dir, name[len(pfx):])]
    else:
        return [p_join(source_dir, name), p_join(link_dir, name)]

def isdot(name, exclude):
    """Verify if name is a dotfile."""
    if name[0] == '.' and name not in exclude:
        return True
    else:
        return False

# parse args
description='Create symlinks in the home directory pointing to dotfiles'
epilog='Documentation: https://github.com/bmweiner/dotlink'
parser = argparse.ArgumentParser(description=description, epilog=epilog)
parser.add_argument('dotfiles', nargs='?', default=os.getcwd(),
                    help='dotfiles directory (default: current directory)')
parser.add_argument('-p', metavar='prefix',
                    help='dotpends prefix')
parser.add_argument('-dp', metavar='dotpends',
                    help='dotpends directory (default: dotfiles/dotpends)')
parser.add_argument('-m', metavar='manifest',
                    help='linking manifest (optional)')
parser.add_argument('-e', nargs='+',
                    help='dotfiles to exclude, adds to std list (ex: .git)')
parser.add_argument('-f', action='store_true',
                    help='overwrite existing symlinks')
parser.add_argument('-v', action='version', version='%(prog)s 0.1')
args = parser.parse_args()
args.df = args.dotfiles

# excluded dotfiles
bad = ['.git', '.gitignore', '.DS_Store']
if args.e:
    bad = bad + args.e

# validate args
dir_args = [args.df, args.dp]
for val in dir_args:
    if val and not os.path.isdir(val):
        path_error(val)
file_args = [args.m]
for val in file_args:
    if val and not os.path.isfile(val):
        path_error(val)

# check if called from home dir
if os.path.samefile(args.df, os.path.expanduser('~')):
    args.df = os.path.join(args.df, 'dotfiles')

# search for dotpends if None
if args.p and not args.dp:
    if 'dotpends' in os.listdir(args.df):
        args.dp = os.path.join(args.df, 'dotpends')

# build manifest
if args.m:
    with open(args.m) as f:
        manifest = list(csv.reader(f))
else:
    src = args.df
    lnk = os.path.expanduser('~')
    manifest = [mline(f, src, lnk) for f in os.listdir(src) if isdot(f, bad)]
    if args.p and args.dp:
        src = args.dp
        for f in os.listdir(src):
            if f.startswith(args.p):
                manifest.append(mline(f, src, lnk, args.p))

# symlink
linked = []
link_error = []
for source, link_name in manifest:
    if args.f and os.path.islink(link_name):
        try:
            os.unlink(link_name)
        except:
            print('WARN: failed to unlink: {}'.format(link_name))
    if win:
        try:
            win32file.CreateSymbolicLink(link_name, source)
            linked.append(link_name)
        except pywintypes.error as err:
            if err.winerror == 183:
                link_error.append(['Name Exists', link_name])
            elif err.winerror == 1314:
                print('Permission Error: must run as administrator')
                raise SystemExit()
    else:
        try:
            os.symlink(source, link_name)
            linked.append(link_name)
        except OSError as err:
            if err.errno == 17:
                link_error.append(['Name Exists', link_name])

# print report
if not linked and not link_error:
    print('Linked: 0')
    print('No dotfiles in: {}'.format(args.df))
else:
    print('Linked: {}, Failed: {}'.format(len(linked), len(link_error)))

if linked:
    print('---------------LINKED---------------')
    for link in linked:
        print('Linked: {}'.format(link))

if link_error:
    print('---------------FAILED---------------')
    for err, link in link_error:
        print('Error ({}): {}'.format(err, link))
    print('\nTry `dotlink.py -f` to overwrite existing symlinks')
    print('Note: -f will only overwrite symlinks, actual files or folders ' +
          'must be removed manually.')

# export manifest
path = os.path.join(os.path.expanduser('~'), '.dotlink')
try:
    # python 3
    with open(path, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(manifest)
except TypeError:
    # python 2
    with open(path, 'wb') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(manifest)
