import math
import pprint
import os
import signal
import sys
import time
import datetime
import glob
from influxdb import InfluxDBClient
import requests
from inotify_simple import INotify, flags
from utils import get_changed_lines, convert_line

client = None
dbname = 'cryomonit'
measurement = 'test'


def db_exists():
    '''returns True if the database exists'''
    dbs = client.get_list_database()
    for db in dbs:
        if db['name'] == dbname:
            return True
    return False

def wait_for_server(host, port, nretries=5):
    '''wait for the server to come online for waiting_time, nretries times.'''
    url = 'http://{}:{}'.format(host, port)
    waiting_time = 1
    for i in range(nretries):
        try:
            requests.get(url)
            return 
        except requests.exceptions.ConnectionError:
            print('waiting for', url)
            time.sleep(waiting_time)
            waiting_time *= 2
            pass
    print('cannot connect to', url)
    sys.exit(1)

def connect_db(host, port, reset):
    '''connect to the database, and create it if it does not exist'''
    global client
    print('connecting to database: {}:{}'.format(host,port))
    client = InfluxDBClient(host, port, retries=5, timeout=1)
    wait_for_server(host, port)
    create = False
    if not db_exists():
        create = True
        print('creating database...')
        client.create_database(dbname)
    else:
        print('database already exists')
    client.switch_database(dbname)
    if not create:
        if reset =='all':
            print('deleting entries of :', measurement)
            client.delete_series(measurement=measurement)
        else:
            client.delete_series(measurement=measurement,tags={'setup':reset})

def get_entries():
    '''returns all entries in the database.'''
    results = client.query('select * from {}'.format(measurement))
    # we decide not to use the x tag
    return list(results[(measurement, None)])





def fill_with_folder(folderpath, setupname, parameter, timezone):
    ''' glob folder starting with 20 and readlines for each of them'''
    files = glob.glob(folderpath+'20*')
    for f in files:
        if f.endswith('~') or f.endswith('diff'):
            continue
        with open(f,'r') as infile:
            lines = infile.readlines()
            fill_dB_with_line(f, lines, setupname, param, timezone)

def fill_dB_with_line(fname, addedlines, setupname, param, timezone):
    '''function to convert one string line to a data to be filled in the database
    the format is the one explained in the readme file
    '''
    for line in addedlines:
        [meastime, meas] = convert_line(fname, line, timezone)
        data = [{
            'measurement':measurement,
            'time':meastime,
            'tags': {
                'setup' : setupname
                },
                'fields' : {
                    param : meas
                    },
            }]
        client.write_points(data)
        pprint.pprint(data)

if __name__ == '__main__':
    import sys
    import difflib
    from optparse import OptionParser

    parser = OptionParser('%prog [OPTIONS] <host> <port> <datafolder> <setupname> <param>')
    parser.add_option(
        '-r', '--reset', dest='reset',
        help='reset database',
        default='',
        type = 'string',
        )
    parser.add_option(
        '-t', '--timezone', dest='timezone',
        help='pytz time zone where the measurement were done',
        type='string',
        default='UTC',
        )
    options, args = parser.parse_args()
    
    if len(args)!=5:
        parser.print_usage()
        print('please specify two arguments')
        sys.exit(1)
    host, port, datafolder, setupname, param = args
    connect_db(host, port, options.reset)
    def signal_handler(sig, frame):
        print()
        print('stopping')
        pprint.pprint(get_entries())
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)


    inotify = INotify() 
    watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF
    wd = inotify.add_watch(datafolder, watch_flags)
    folder = datafolder
    if options.reset != '':
        fill_with_folder(folder, setupname, param,options.timezone)
    while(True):
        time.sleep(5)
        listofchangedfiles = []
        for event in inotify.read():        
            if '#' in event.name or '~'  in event.name or 'diff' in event.name:
                #print ('exluded filename = ', event.name)
                continue    
            else: 
                print ('event.name = ',event.name )
                if event.mask in [2,256] :
                    changedfile = folder + '/' + event.name
                if changedfile not in listofchangedfiles:
                    listofchangedfiles.append(changedfile)  
        print ('listofchangedfiles = ', listofchangedfiles)
        for changedfile in listofchangedfiles:
            print('changedfile  = ' , changedfile)
            addedlines = get_changed_lines(changedfile)
            print ('addedline = ', addedlines)   
            fill_dB_with_line(changedfile, addedlines, setupname, param, options.timezone)    


        # for flag in flags.from_mask(event.mask):
        #     print('    ', str(flag))