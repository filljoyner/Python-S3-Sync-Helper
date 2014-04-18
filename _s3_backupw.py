import os
import sys
from time import sleep, gmtime, strftime
from multiprocessing.pool import ThreadPool

sys.path.append(os.getcwd() + "\\App")

import App

from Tkinter import *
import ttk
import tkFileDialog


class Backup():
    sep = '<<--|||-->>'
    threads = 10
    log_file = ''
    sLog = None
    files = None

    _dir_local = ''
    _dir_s3 = ''

    # GET IT ALL STARTED
    def __init__(self, root):
        self.FileStack = App.FileStack()
        self.Utility = App.Utility()

        # data file
        self.data_file = os.getcwd() + '/App/Store/data'

        # data file
        self.create_data()

        self.win = root
        self.win.title("S3 Backup")
        
        self.status = StringVar()
        self.api_access = StringVar()
        self.api_secret = StringVar()
        self.api_bucket = StringVar()

        self._api_access = ''
        self._api_secret = ''
        self._api_bucket = ''
        
        self.dir_s3 = StringVar()
        self.dir_local = StringVar()

        self.num_threads = StringVar()
        self.num_threads.set(10)

        self.txt_log = StringVar()

        self.read_data()

        self.build()



    # DATA FILE
    # create data file
    def create_data(self):
        self.FileStack.touch(self.data_file)


    # read data file
    def read_data(self):
        content = open(self.data_file, 'r')
        data = content.read().split(self.sep)
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
            threads = self.threads


        self.api_access.set(access)
        self.api_secret.set(secret)
        self.api_bucket.set(bucket)
        self.dir_s3.set(dir_s3)
        self.dir_local.set(dir_local)
        self.num_threads.set(threads)


    # write data file
    def write_data(self):
        if self.api_access != '' and self.api_secret != '':
            self._api_access = self.api_access.get()
            self._api_secret = self.api_secret.get()
            self._api_bucket = self.api_bucket.get()

            content = self.api_access.get() + self.sep + self.api_secret.get() + self.sep + self.api_bucket.get() + self.sep + self.dir_s3.get() + self.sep + self.dir_local.get() + self.sep + str(self.num_threads.get())
            f = open(self.data_file, 'w')
            f.write(content)
            f.close()


    # LOG FILE
    def create_log(self):
        self.FileStack.touch(self.log_file)

    def log(self, msg=None):
        if msg == None:
            return

        file = open(self.log_file, 'a')
        txt = '[' + self.Utility.timestamp() + '] ' + msg + "\n"
        file.write(txt)
        file.close()


    def log_screen(self, msg=None):
        if msg == None:
            msg = ''

        msg+= '\n'

        self.sLog['state'] = 'normal'
        txt = self.sLog.get('0.0', END)
        self.sLog.insert(END, msg)
        self.sLog['state'] = 'disabled'


    
    # GET LOCAL DIRECTORY
    def get_dir_local(self):
        dir_output = tkFileDialog.askdirectory()
        self.dir_local.set(dir_output)


    # get number of entries in a list of lists
    def get_nested_list_size(self, _list):
        _len = 0
        for l in _list:
            _len+= len(l)
        return _len
    
    

    # BUILD INTERFACE
    def build(self):
        self.mainframe = ttk.Frame(self.win).grid(column=0,row=0,sticky=(N,W,S,E), padx=5,pady=5)

        ttk.Label(self.mainframe, text="S3 API Access Key").grid(column=0,row=1,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=self.api_access).grid(column=1,row=1,sticky=(W,E), pady=5, padx=5)

        ttk.Label(self.mainframe, text="S3 API Access Secret").grid(column=0,row=2,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=self.api_secret).grid(column=1,row=2,sticky=(W,E), pady=5, padx=5)
        
        ttk.Label(self.mainframe, text="S3 Bucket Name").grid(column=0,row=3,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=self.api_bucket).grid(column=1,row=3,sticky=(W,E), pady=5, padx=5)

        ttk.Label(self.mainframe, text="S3 Directory (Optional)").grid(column=0,row=4,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=self.dir_s3).grid(column=1,row=4,sticky=(W,E), pady=5, padx=5)
        
        ttk.Label(self.mainframe, text="Directory").grid(column=0,row=5,sticky=(W), pady=5, padx=5)
        ttk.Entry(self.mainframe, width=35, textvariable=self.dir_local).grid(column=1,row=5, pady=5, padx=5, sticky=(W,E))
        ttk.Button(self.mainframe, text="   Browse   ", command=self.get_dir_local).grid(column=2,row=5,sticky=(W), pady=5, padx=5)

        ttk.Label(self.mainframe, text="Threads").grid(column=0,row=6,stick=(W), pady=5, padx=5)
        Spinbox(self.mainframe, from_=1, to=50, textvariable=self.num_threads).grid(column=1,row=6,sticky=(W,E), pady=5, padx=5)
        
        ttk.Button(self.mainframe, text="   Backup   ", command=self.start_backup).grid(column=1,row=7,sticky=(W), pady=5, padx=5)

        ttk.Label(self.mainframe, text="Log").grid(column=0,row=8,stick=(N,W), pady=5, padx=5)
        self.sLog = Text(self.mainframe, width=80, height=10, wrap='none', state='disabled')
        self.sLog.grid(column=1,columnspan=2,row=8,sticky=(W), pady=5, padx=5)
    
    
    # BACKUP
    def start_backup(self):
        self.write_data()

        # initialize variables
        self.time_format = "%Y-%m-%d %H:%M:%S +0000"

        self.upload_num = 0
        self.file_count = 0
        self.file_pad = 0
        self.file_num = 0
        self.updated_num = 0
        self.present_num = 0
        self.empty_num = 0
        self.upload_size = 0
        self.fail_file = 0

        # log file
        log_file = 'log-' + self.Utility.timestamp() + '.txt'
        self.log_file = os.getcwd() + '/Logs/' + log_file.replace(' +0000', '').replace(':', '_')
        self.create_log()

        if self.dir_s3.get() != '':
            self._dir_s3 = self.dir_s3.get().replace('\\', '/')

        if self.dir_local.get() != '':
            self._dir_local = self.dir_local.get().replace('\\', '/')

        if self._dir_s3 == '':
            self._dir_s3 = os.path.basename(self._dir_local)

        self.threads = int(self.num_threads.get())
        
        self.log_screen('local folder: ' + self._dir_local)
        self.log_screen('   s3 folder: ' + self._dir_s3)
        self.log_screen('-----------------------------------------------------')
        self.log_screen()
        self.log_screen('Getting local file list...')
        self.log_screen()
        
        # get files in local dir (aka workspace)
        self.files = self.FileStack.folder_read(self._dir_local, self.threads)

        self.start_time = strftime(self.time_format, gmtime())

        if self.files:
            self.S3 = App.S3(self.api_access.get(), self.api_secret.get())
            
            self.file_num = self.get_nested_list_size(self.files)
            self.file_pad = len(str(self.file_num))

            self.log_screen('-----------------------------------------------------')
            self.log_screen('Processing ' + str(self.file_num) + ' file(s)')
            self.log_screen('-----------------------------------------------------')
            self.log_screen()

            if self.S3.connect(self._api_bucket):
                for _files in self.files:
                    pool = ThreadPool(processes=self.threads)
                    
                    try:
                        pool.map(s3_upload, _files)
                        pool.close()
                        pool.join()
                    except:
                        pool.close()
                        pool.join()
                        for f in _files:
                            self.log(f + ' | Pool map error')
                            self.fail_file+= 1
                            self.log_screen(f + ' | ERROR: Pool map')

            else:
                self.log_screen('S3 Connection Error: Check credentials, permissions and bucket name')

        else:
            self.log_screen('-----------------------------------------------------')
            self.log_screen('No Files to Process')
            self.log_screen('-----------------------------------------------------')
            self.log_screen()


        _found_num = str(self.file_num).rjust(self.file_pad)
        _upload_num = str(self.upload_num).rjust(self.file_pad)
        _present_num = str(self.present_num).rjust(self.file_pad)
        _updated_num = str(self.updated_num).rjust(self.file_pad)
        _empty_num = str(self.empty_num).rjust(self.file_pad)
        _fail_num = str(self.fail_file).rjust(self.file_pad)
        _total_num = str(self.upload_num + self.present_num + self.updated_num + self.empty_num + self.fail_file).rjust(self.file_pad)
        _upload_size = round((float(uploaded_size) / 1024) / 1024, 2)


        self.log_screen('')
        self.log_screen('-----------------------------------------------------')
        self.log_screen('Details - ' + _total_num + '/' + _found_num + ' Processed')
        self.log_screen('-----------------------------------------------------')
        self.log_screen(_upload_num +  ' file(s) Uploaded       (New)')
        self.log_screen(_present_num + ' file(s) Present in S3  (Exists)')
        self.log_screen(_updated_num + ' file(s) Updated in S3  (Overwritten)')
        self.log_screen(_empty_num +   ' file(s) Skipped        (0 byte)')
        self.log_screen(_fail_num +    ' file(s) Failed         (Check Log File)')
        self.log_screen('')
        self.log_screen(' Started: ' + str(self.start_time))
        self.log_screen('Finished: ' + str(strftime(self.time_format, gmtime())))
        self.log_screen('Uploaded: ' + str(_upload_size) + 'MB')
        self.log_screen('  Failed: ' + str(_upload_size) + 'MB')
        self.log_screen('-----------------------------------------------------')



    # upload function used for multiprocessing
    def s3_upload(self, _file=None):
        s3_file = self._dir_s3 + '/' + _file[len(self._dir_local)+1:].replace('\\', '/')
        s3_file_show = '...' + s3_file[-40:]

        local_filesize = self.FileStack.filesize(_file)
        s3_filesize = self.S3.size(s3_file)

        # if local filesize is more than 0
        if local_filesize:
            # if s3_filesize is not present (key not used), upload file
            if s3_filesize == None:
                msg = self.S3.upload(_file, s3_file)
                if msg != None:
                    self.log(msg)
                    self.fail_file+= 1
                    self.log_screen(str(self.file_count).rjust(self.file_pad) + '/' + str(self.file_num) + ' | ERROR: ' + s3_file_show)
                else:
                    self.upload_num += 1
                    self.file_count+= 1
                    self.uploaded_size+= local_filesize
                    self.log_screen(str(self.file_count).rjust(self.file_pad) + '/' + str(self.file_num) + ' | Upload: ' + s3_file_show)

            # if local filesize is not the same as s3 filesize, upload file
            elif local_filesize != s3_filesize:
                msg = self.S3.upload(_file, s3_file)
                if msg != None:
                    self.log(msg)
                    self.fail_file+= 1
                    self.log_screen(str(self.file_count).rjust(self.file_pad) + '/' + str(self.file_num) + ' | ERROR (s3!=local): ' + s3_file_show)
                else:
                    updated_num += 1
                    self.file_count+= 1
                    self.uploaded_size+= local_filesize
                    self.log_screen(str(self.file_count).rjust(self.file_pad) + '/' + str(self.file_num) + ' | Upload (s3!=local): ' + s3_file_show)

            # if local filesize and s3 filesize are the same, file must be same
            elif local_filesize == s3_filesize:
                self.present_num += 1
                self.file_count+= 1
                #print str(self.file_count).rjust(self.file_pad) + '/' + str(self.file_num) + ' | Present (' + str(local_filesize) + '==' + str(s3_filesize) + '): ' + s3_file_show
                self.log_screen(str(self.file_count).rjust(self.file_pad) + '/' + str(self.file_num) + ' | Present: ' + s3_file_show)

        # give local file size is 0 error
        else:
            self.empty_num+= 1
            self.file_count+= 1
            self.log_screen(str(self.file_count).rjust(self.file_pad) + '/' + str(self.file_num) + ' | Local size 0: ' + s3_file_show)


global app

def s3_upload(_file=None):
    global app
    return app.s3_upload(_file)


root = Tk()
app = Backup(root)
root.mainloop()