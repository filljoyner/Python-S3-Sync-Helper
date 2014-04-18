# ==============================================================================
# Python S3 Sync Helper
# ------------------------------------------------------------------------------
# Written Hastily by:   Philip Joyner
# Version:              0.3
# Last Updated:         2014-04-16
# Requirements:         Python 2.7, Scandir & Boto
# ------------------------------------------------------------------------------


# IMPORTS
import os
import sys
from time import gmtime, strftime
from multiprocessing.pool import ThreadPool

sys.path.append(os.getcwd() + "\\App")

import App
from config import Config



# FUNCTIONS
def create_data():
    global data_file
    FS.touch(data_file)


def read_data():
    global data_file
    content = open(data_file, 'r')
    data = content.read().split('<|>')
    content.close()


def write_data(varA=None, varB=None):
    if varA != None and varB != None:
        global data_file
        content = varA + '<|>' + varB
        f = open(data_file, 'w')
        f.write(content)
        f.close()


def create_log(_log_file=None):
    global log_file
    global FS
    log_file = _log_file
    FS.touch(log_file)

def log(msg=None):
    if msg == None:
        return

    global log_file, utility

    file = open(log_file, 'a')
    txt = '[' + utility.timestamp() + '] ' + msg.encode('utf-8') + "\n"
    file.write(txt)
    file.close()



# get number of entries in a list of lists
def get_nested_list_size(_list):
    _len = 0
    for l in _list:
        _len+= len(l)
    return _len


# upload function used for multiprocessing
def global_upload(_file=None):
    global return_prints, file_prefix, workspace, FS, s3, upload_num, file_count
    global file_pad, file_num, updated_num, present_num, empty_num, uploaded_size
    global fail_file

    s3_file = file_prefix + '/' + _file[len(workspace)+1:].replace('\\', '/')
    s3_file_show = '...' + s3_file[-45:].encode('utf-8')

    local_filesize = FS.filesize(_file)
    s3_filesize = s3.size(s3_file)

    # if local filesize is more than 0
    if local_filesize:
        # if s3_filesize is not present (key not used), upload file
        if s3_filesize == None:
            msg = s3.upload(_file, s3_file)
            if msg != None:
                log(msg)
                fail_file+= 1
                print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | ERROR: ' + s3_file_show
            else:
                upload_num += 1
                file_count+= 1
                uploaded_size+= local_filesize
                print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Upload: ' + s3_file_show

        # if local filesize is not the same as s3 filesize, upload file
        elif local_filesize != s3_filesize:
            msg = s3.upload(_file, s3_file)
            if msg != None:
                log(msg)
                fail_file+= 1
                print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | ERROR (s3!=local): ' + s3_file_show
            else:
                updated_num += 1
                file_count+= 1
                uploaded_size+= local_filesize
                print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Upload (s3!=local): ' + s3_file_show

        # if local filesize and s3 filesize are the same, file must be same
        elif local_filesize == s3_filesize:
            present_num += 1
            file_count+= 1
            #print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Present (' + str(local_filesize) + '==' + str(s3_filesize) + '): ' + s3_file_show
            print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Present: ' + s3_file_show

    # give local file size is 0 error
    else:
        empty_num+= 1
        file_count+= 1
        print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Local size 0: ' + s3_file_show




# INITIALIZE VARIABLES
# globals
global return_prints, file_prefix, workspace, FS, s3, upload_num, file_count
global file_pad, file_num, updated_num, present_num, empty_num, uploaded_size
global fail_file, log_file, utility, data_file

# set variables from config file
access = Config['s3_access']
secret = Config['s3_secret']
bucket = Config['s3_bucket']
basefolder = Config['s3_folder']
workspace = Config['local_dir']
basename = os.path.basename(workspace)
threads = Config['upload_threads']

# more variables please
return_prints = []
time_format = "%Y-%m-%d %H:%M:%S +0000"
start_time = strftime(time_format, gmtime())
file_pad = 0
file_num = 0
upload_num = 0
present_num = 0
updated_num = 0
empty_num = 0
file_count = 0
uploaded_size = 0
fail_file = 0

# fix the paths if the slash is heading in the wrong direction
if basefolder:
    basefolder = basefolder.replace('\\', '/')

if workspace:
    workspace = workspace.replace('\\', '/')

# file_prefix is given to all s3 keys, by default it is the workspace
# folder name unless already set by config s3_folder
file_prefix = basename
if basefolder != None:
    file_prefix = basefolder

# instantiate classes

FS = App.FileStack()
s3 = App.S3(access, secret)
utility = App.Utility()

# create log file
log_file = '/log-' + utility.timestamp() + '.txt'
log_file = os.getcwd() + '/Logs' + log_file.replace(' +0000', '').replace(':', '_')

data_file = os.getcwd() + '/App/Store/data'

create_log(log_file)


print ''
print '-----------------------------------------------------'
print 'Python S3 Sync Helper'
print '-----------------------------------------------------'
print ''
print 'local folder: ' + workspace
print '   s3 folder: ' + file_prefix
print ''
print '-----------------------------------------------------'
print ''
print 'Getting local file list...'
print ''

# get files in local dir (aka workspace)
files = FS.folder_read(workspace, threads)


if files:
    file_num = get_nested_list_size(files)
    file_pad = len(str(file_num))

    print '-----------------------------------------------------'
    print 'Processing ' + str(file_num) + ' file(s)'
    print '-----------------------------------------------------'
    print ''

    if s3.connect(bucket):
        for _files in files:
            pool = ThreadPool(processes=threads)
            
            try:
                pool.map(global_upload, _files)
                pool.close()
                pool.join()
            except:
                for f in _files:
                    log(f + ' | Pool map error')
                    fail_file+= 1
                    print f.encode('utf-8') + ' | ERROR: Pool map'
                pool.close()
                pool.join()

            pool.terminate()

            
    else:
        print 'S3 Connection Error: Check credentials, permissions and bucket name'

else:
    print '-----------------------------------------------------'
    print 'No Files to Process'
    print '-----------------------------------------------------'
    print ''




# DISPLAY FINAL DETAILS RESULTS
# figure out number display size for presentation... don't worry about this stuff
_found_num = str(file_num).rjust(file_pad)
_upload_num = str(upload_num).rjust(file_pad)
_present_num = str(present_num).rjust(file_pad)
_updated_num = str(updated_num).rjust(file_pad)
_empty_num = str(empty_num).rjust(file_pad)
_fail_num = str(fail_file).rjust(file_pad)
_total_num = str(upload_num + present_num + updated_num + empty_num + fail_file).rjust(file_pad)
_upload_size = round((float(uploaded_size) / 1024) / 1024, 2)


print ''
print '-----------------------------------------------------'
print 'Details - ' + _total_num + '/' + _found_num + ' Processed'
print '-----------------------------------------------------'
print _upload_num +  ' file(s) Uploaded       (New)'
print _present_num + ' file(s) Present in S3  (Exists)'
print _updated_num + ' file(s) Updated in S3  (Overwritten)'
print _empty_num +   ' file(s) Skipped        (0 byte)'
print _fail_num +    ' file(s) Failed         (Check Log File)'
print ''
print ' Started: ' + str(start_time)
print 'Finished: ' + str(strftime(time_format, gmtime()))
print 'Uploaded: ' + str(_upload_size) + 'MB'
print '  Failed: ' + str(_upload_size) + 'MB'
print '-----------------------------------------------------'