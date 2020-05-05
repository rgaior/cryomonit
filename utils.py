import os
import datetime
import difflib

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

from pytz import timezone
import pytz
def convert_line(fname, line, pytztimezone):
    localtz = timezone(pytztimezone)
    timeinday = line.split(' ')[0]
    timeinday = timeinday.split(':')
    meas = float(line.split(' ')[1])

    fname = fname[fname.rfind('/')+1:]
    meastime = datetime.datetime(
        year = int(fname[:4]), 
        month=int(fname[4:6]),
        day=int(fname[6:8]),
        hour=int(timeinday[0]),
        minute=int(timeinday[1]),
        second=int(timeinday[2]))
    meastime_dt = localtz.localize(meastime,is_dst=None)
    utc_dt = meastime_dt.astimezone(pytz.utc)
    return [utc_dt,meas]


def get_changed_lines(changedfile):
    '''get the lines that were added in the file compared to a previous one
        and updates the diff file
        if the diff file didn't exist before it is created.
    '''
    addedline = []
    if not os.path.exists(changedfile+ '_diff'):
            touch(changedfile+'_diff')
    text = open(changedfile).readlines()
    textdiff = open(changedfile+'_diff').readlines()
    lines = difflib.unified_diff(textdiff, text)
    for line in lines:
        print('line = ', line)
        excludedsign = ['---', '+++', '@@','++']
        check = any(x in line for x in excludedsign)
        
        if check == True: 
            continue   
        else:
            print ('0000 addedline = ', line[1:])
            if line.startswith('+'):
                print ('addedline = ', line[1:])
                if line != '+\n':
                    addedline.append(line[1:])
    with open(changedfile+'_diff','a') as f:
        for l in addedline:
            f.write(l)
    return addedline