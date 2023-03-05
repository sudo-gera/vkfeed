''':'
echo -en "loading...\r"
apt update -yqqq
apt install python git -yqqq
python3 $0 $@
exit
':'''
from subprocess import *
from sys import argv
from pathlib import Path
from os.path import *
from os import *
open_ = open
home = str(Path.home())+'/'
path = str(abspath(dirname(argv[0])))
if path[-1] != '/':
    path += '/'
try:
    mkdir(home+'.vkfeed')
except:
    pass
chdir(home+'.vkfeed')
open_('path', 'w').write(path)
try:
    run(['apt', 'download', 'termux-api', '-yqqq'])
except:
    print('installation failed. check internet connection. if it does not help, turn on mobile data and wifi hotspot and try again')
termux = listdir('.')
termux = [w for w in termux if w.endswith('.deb')]
termux.sort(key=getmtime)
termux = termux[-1]
try:
    run(['apt', 'install', abspath(termux), '-yqqq'])
except:
    print('installation failed. turn on mobile data and wifi hotspot and try again')
chdir(path)
run(['git', 'pull', '--no-edit', '-q'])
try:
    run(['ln', '-s', path+'news.py', home+'../usr/bin/vkfeed'], stderr='PIPE')
except:
    pass
print('installation complete. now you can run \x1b[32mvkfeed\x1b[0m command')
