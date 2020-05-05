import time
from datetime import date
import datetime
import sys
folder = sys.argv[1]
#folder = '/Users/gaior/DAMIC/code/monitoring/app/testdata/'

while True:
    time.sleep(1)
    today = date.today()

    # dd/mm/YY
    d = today.strftime("%Y%m%d")
    fname = str(d)
    outfilename = folder + fname
    with open(outfilename, 'a') as out_file:
        now = datetime.datetime.now()
        line = str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + ' ' + str(now.microsecond) + '\n'
        out_file.write(line)
    
    