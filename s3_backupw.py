import os
import sys
from time import sleep, gmtime, strftime
from multiprocessing.pool import ThreadPool

sys.path.append(os.getcwd() + "\\App")

import App

from Tkinter import *
import ttk
import tkFileDialog




# ----------------------------------------------
# GLOBALS
# ----------------------------------------------
global frm_api_access, frm_api_secret, frm_api_bucket, frm_dir_s3, frm_dir_local, frm_threads, frm_log
global FS, utility, data_file, sep, num_threads
# ----------------------------------------------
# END GLOBALS
# ----------------------------------------------



# ----------------------------------------------
# INSTANTIATE
# ----------------------------------------------
FS               = App.FileStack()
utility          = App.Utility()
data_file        = os.getcwd() + '/App/Store/data'
sep              = '<<--|||-->>'
num_threads      = 10
# ----------------------------------------------
# END INSTANTIATE
# ----------------------------------------------





# ----------------------------------------------
# DATA FILE
# ----------------------------------------------
# create data file
def create_data(data_file):
    global FS
    FS.touch(data_file)


# read data file
def read_data(data_file):
    global frm_api_access, frm_api_secret, frm_api_bucket, frm_dir_s3, frm_dir_local, frm_threads
    global sep, num_threads

    content = open(data_file, 'r')
    data = content.read().split(sep)
    content.close()

    access = ''
    secret = ''
    bucket = ''
    dir_s3 = ''
    dir_local = ''
    threads = ''

    try:
        access = data[0]
        secret = data[1]
    except:
        access = ''
        secret = ''

    try:
        bucket = data[2]
    except:
        bucket = ''

    try:
        dir_s3 = data[3]
    except:
        dir_s3 = ''

    try:
        dir_local = data[4]
    except:
        dir_local = ''

    try:
        threads = int(data[5])
    except:
        threads = num_threads


    frm_api_access.set(access)
    frm_api_secret.set(secret)
    frm_api_bucket.set(bucket)
    frm_dir_s3.set(dir_s3)
    frm_dir_local.set(dir_local)
    frm_threads.set(threads)


# write data file
def write_data(data_file):
    global frm_api_access, frm_api_secret, frm_api_bucket, frm_dir_s3, frm_dir_local, frm_threads
    global sep

    api_access = frm_api_access.get()
    api_secret = frm_api_secret.get()
    api_bucket = frm_api_bucket.get()
    dir_s3     = frm_dir_s3.get()
    dir_local  = frm_dir_local.get()
    threads    = frm_threads.get()
    
    content = api_access + sep + api_secret + sep + api_bucket + sep + dir_s3 + sep + dir_local + sep + threads
    f = open(data_file, 'w')
    f.write(content)
    f.close()

# ----------------------------------------------
# END DATA FILE
# ----------------------------------------------




# ----------------------------------------------
# LOG
# ----------------------------------------------
def create_log(log_file):
    global FS, utility
    FS.touch(log_file)

def log(log_file, msg=None):
    if msg == None:
        return

    file = open(log_file, 'a')
    txt = '[' + utility.timestamp() + '] ' + msg + "\n"
    file.write(txt)
    file.close()


def log_screen_clear():
    global frm_log

    frm_log['state'] = 'normal'
    frm_log.delete('0.0', END)
    frm_log['state'] = 'disabled'


def log_screen(msg=None):
    global frm_log

    if msg == None:
        msg = ''

    msg+= '\n'

    frm_log['state'] = 'normal'
    #txt = frm_log.get('0.0', END)
    frm_log.insert(END, msg)
    frm_log['state'] = 'disabled'
# ----------------------------------------------
# END LOG
# ----------------------------------------------





# ----------------------------------------------
# BACKUP
# ----------------------------------------------
def backup():
    global files
    start_backup()

def start_backup():
    global frm_dir_s3, frm_dir_local, frm_threads
    global data_file, log_file, utility, workspace, threads, files

    log_screen_clear()

    log_file = '/log-' + utility.timestamp() + '.txt'
    log_file = os.getcwd() + '/Logs' + log_file.replace(' +0000', '').replace(':', '_')

    write_data(data_file)
    create_log(log_file)

    basefolder = frm_dir_s3.get()
    workspace = frm_dir_local.get()
    basename = os.path.basename(workspace)

    threads = int(frm_threads.get())

    if basefolder != '':
        basefolder = basefolder.replace('\\', '/')

    if workspace != '':
        workspace = workspace.replace('\\', '/')

    file_prefix = basename
    if basefolder != '':
        file_prefix = basefolder

    log_screen('')
    log_screen('local folder: ' + workspace)
    log_screen('   s3 folder: ' + file_prefix)
    log_screen('')
    log_screen('-----------------------------------------------------')
    log_screen('')
    log_screen('Getting local file list...')
    log_screen('')

    files = get_files(workspace, threads)


def get_files(_dir, _threads):
    global FS
    return FS.folder_read(_dir, _threads)
# ----------------------------------------------
# END BACKUP
# ----------------------------------------------



class Backup():
    # GET IT ALL STARTED
    def __init__(self, root):
        global frm_api_access, frm_api_secret, frm_api_bucket, frm_dir_s3, frm_dir_local, frm_threads, frm_log

        frm_api_access   = StringVar()
        frm_api_secret   = StringVar()
        frm_api_bucket   = StringVar()
        frm_dir_s3       = StringVar()
        frm_dir_local    = StringVar()
        frm_threads      = StringVar()
        frm_log          = None

        self.FileStack = App.FileStack()
        self.Utility = App.Utility()

        # data file
        self.data_file = os.getcwd() + '/App/Store/data'

        self.win = root
        self.win.title("S3 Backup")
        
        self.build()


    
    # GET LOCAL DIRECTORY
    def get_dir_local(self):
        dir_output = tkFileDialog.askdirectory()
        self.dir_local.set(dir_output)
    
    

    # BUILD INTERFACE
    def build(self):
        global frm_api_access, frm_api_secret, frm_api_bucket, frm_dir_s3, frm_dir_local, frm_threads, frm_log

        self.mainframe = ttk.Frame(self.win).grid(column=0,row=0,sticky=(N,W,S,E), padx=5,pady=5)

        ttk.Label(self.mainframe, text="S3 API Access Key").grid(column=0,row=1,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=frm_api_access).grid(column=1,row=1,sticky=(W,E), pady=5, padx=5)

        ttk.Label(self.mainframe, text="S3 API Access Secret").grid(column=0,row=2,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=frm_api_secret).grid(column=1,row=2,sticky=(W,E), pady=5, padx=5)
        
        ttk.Label(self.mainframe, text="S3 Bucket Name").grid(column=0,row=3,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=frm_api_bucket).grid(column=1,row=3,sticky=(W,E), pady=5, padx=5)

        ttk.Label(self.mainframe, text="S3 Directory (Optional)").grid(column=0,row=4,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=frm_dir_s3).grid(column=1,row=4,sticky=(W,E), pady=5, padx=5)
        
        ttk.Label(self.mainframe, text="Directory").grid(column=0,row=5,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=frm_dir_local).grid(column=1,row=5, pady=5, padx=5, sticky=(W,E))
        ttk.Button(self.mainframe, text="   Browse   ", command=self.get_dir_local).grid(column=2,row=5,sticky=(W), pady=5, padx=5)

        ttk.Label(self.mainframe, text="Threads").grid(column=0,row=6,stick=(W), pady=5, padx=5)
        Spinbox(self.mainframe, from_=1, to=50, textvariable=frm_threads).grid(column=1,row=6,sticky=(W,E), pady=5, padx=5)
        
        ttk.Button(self.mainframe, text="   Backup   ", command=backup).grid(column=1,row=7,sticky=(W), pady=5, padx=5)

        ttk.Label(self.mainframe, text="Log").grid(column=0,row=8,stick=(N,W), pady=5, padx=5)
        frm_log = Text(self.mainframe, width=80, height=10, wrap='none', state='disabled')
        frm_log.grid(column=1,columnspan=2,row=8,sticky=(W), pady=5, padx=5)



# ----------------------------------------------
# INITIAL FUNCTION CALLS
# ----------------------------------------------
create_data(data_file)
# ----------------------------------------------
# INITIAL FUNCTION CALLS
# ----------------------------------------------



# ----------------------------------------------
# GUI
# ----------------------------------------------
root = Tk()
app = Backup(root)
# ----------------------------------------------
# END GUI
# ----------------------------------------------



# ----------------------------------------------
# AFTER GUI FUNCTIONS
# ----------------------------------------------
read_data(data_file)
root.mainloop()
# ----------------------------------------------
# END AFTER GUI FUNCTIONS
# ----------------------------------------------