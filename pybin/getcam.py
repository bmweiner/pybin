import sys
import os
import ConfigParser
import datetime
from ftplib import FTP

def help_msg():
    msg = """
usage: getcam.py [-h] [day] [day time]

Get Amcrest Images for a specific day or a Video for a specific
day and time. Returns images for today by default.

optional arguments:
 -h, --help: show this help message and exit
 day: day of image or video, possible values:
   today, yesterday
   YYYY-MM-DD (ISO-8601)
   0, 1, 2, ..., n: days ago
 time: time of video, possible values:
   hh:mm:ss (ISO-8601)
"""
    return msg

def parse_args(args):
    """Parse sys.argv."""
    l = {}
    if len(args) == 1:  # no args provided
        l['day'] = (datetime.date.today().strftime('%Y-%m-%d'))
    else:
        # parse day
        if args[1].lower() == 'today':
            l['day'] = (datetime.date.today().strftime('%Y-%m-%d'))
        elif args[1].lower() == 'yesterday':
            d = datetime.date.today() - datetime.timedelta(1)
            l['day'] = (d.strftime('%Y-%m-%d'))
        else:
            try:
                offset = abs(int(args[1]))
                d = datetime.date.today() - datetime.timedelta(offset)
                l['day'] = (d.strftime('%Y-%m-%d'))
            except ValueError:
                d = datetime.datetime.strptime(args[1], '%Y-%m-%d')
                l['day'] = (d.strftime('%Y-%m-%d'))
    if len(args) == 3:
        # parse time
        t = datetime.datetime.strptime(args[2], '%H:%M:%S')
        l['time'] = (t.strftime('%H.%M.%S'))
    return l

def get_config(filename):
    config = ConfigParser.ConfigParser()
    config.read(filename)
    return dict(config.items(config.sections()[0]))

def setup_ftp(cfg):
    ftp = FTP(cfg['host'])
    ftp.login(cfg['user'], cfg['password'])
    ftp.cwd(cfg['directory'])
    return ftp

def images(ftp, day):
    localdir = os.path.join(day, 'jpg')
    try:
        os.makedirs(localdir)
    except OSError:
        pass
    for hour in ftp.nlst(day):
        remotenames = ftp.nlst(os.path.join(day, hour, 'jpg'))
        for remotename in remotenames:
            with open(os.path.join(localdir, remotename), 'wb') as f:
                remotepath = os.path.join(day, hour, 'jpg', remotename)
                ftp.retrbinary('RETR ' + remotepath, f.write)

def video(ftp, day, time):
    localdir = os.path.join(day, 'mp4')
    try:
        os.makedirs(localdir)
    except OSError:
        pass

    hours = [time[:2] + 'hour']
    if hours[0] != '00hour':
        hours.append('{:02d}'.format(int(time[:2]) - 1) + 'hour')
    for hour in hours:
        remotedir = os.path.join(day, hour, 'mp4')
        remotenames = [f for f in ftp.nlst(remotedir) if f.endswith('.mp4')]
        for remotename in remotenames:
            t0 = remotename[:8]
            t1 = remotename[9:17]
            if time >= t0 and time <= t1:
                with open(os.path.join(localdir, remotename), 'wb') as f:
                    remotepath = os.path.join(day, hour, 'mp4', remotename)
                    ftp.retrbinary('RETR ' + remotepath, f.write)

if __name__ == "__main__":
    help_format = ['-h', '--h', '-help', '--help', 'help']
    if len(sys.argv) > 1 and sys.argv[1] in help_format:
        print(help_msg())
        sys.exit()
    args = parse_args(sys.argv)
    cfg = get_config(['.getcam', os.path.expanduser('~/.getcam')])
    ftp = setup_ftp(cfg)
    if len(args) == 1:
        images(ftp, args['day'])
    elif len(args) == 2:
        video(ftp, args['day'], args['time'])
    ftp.close()
