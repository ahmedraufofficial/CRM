import sys,os
INTERP = "/home/ezzataljbour/flaskweb2/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
from webserver import app as application