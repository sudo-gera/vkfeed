import sys
import os
import os.path
import pathlib
home = str(pathlib.Path().home())
repo = os.path.dirname(os.path.realpath(sys.argv[0]))
user_data = os.path.join(repo, 'user_data')
if not os.path.exists(user_data):
    os.mkdir(user_data)

