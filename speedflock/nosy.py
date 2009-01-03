#!/usr/bin/python
import glob,os,stat,time

def checkSum():
    ''' Return a long which can be used to know if any .py files have changed.
    Only looks in the current directory. '''
    val = 0
    for f in (glob.glob ('*.py') + glob.glob('tests/*.py')):
        stats = os.stat (f)
        val += stats [stat.ST_SIZE] + stats [stat.ST_MTIME]
    return val

val = 0
while True:
    if checkSum() != val:
        val = checkSum()
        os.system ('nosetests --with-doctest --with-coverage --cover-package=speedflock --cover-erase -a tags=speedflock')
        for f in glob.glob('*.py'):
            os.system('coverage -a ' + f)
        time.sleep(1)
