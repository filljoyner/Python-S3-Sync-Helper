# IMPORT LIBRARIES
import os
import re
import shutil


class FileStack:

    def mk_dir(self, dir):
        if os.path.isdir(dir) == False:
            os.mkdir(dir)
            
    
    
    # is file
    def is_file(self, filepath):
        if os.path.isfile(filepath):
            return True
        return False


    # is directory
    def is_dir(self, dirpath):
        if os.path.isdir(dirpath):
            return True
        return False
    
    
    
    # touch file
    def touch(self, filepath):
        if os.path.isfile(filepath) == False:
            file = open(filepath, 'w')
            file.write('')
            file.close()
            return True
        return False
    
    
    
    # get file size
    def filesize(self, filepath):
        return os.path.getsize(filepath)
    
    
    
    # replaces text in file
    def file_find_replace(self, file_in, file_out, dicts):
        if len(dicts) > 0:
            # read file_in, create and open file_out
            data = open(file_in).read().decode('ascii', 'ignore')
            new_file = open(file_out, 'w')
            
            for dict in dicts:
                for key in dict:
                    data = re.sub(key,dict[key], data)
        
            # write and close new file
            new_file.write(data)
            new_file.close()


    def folder_read(self, path=None, chunks=False):
        if path == None or self.is_dir(path) == False:
            return False

        fileList = []
        for root, subFolders, files in os.walk(path):
            for file in files:
                fileList.append(os.path.join(root,file))
        
        if fileList:
            if chunks != False:
                return self.__chunks(fileList, chunks)
            return fileList

        return False


    def __chunks(self, l, n):
        _list = []
        for i in xrange(0, len(l), n):
            _list.append(l[i:i+n])
        return _list



    
    
    
    # delete file
    def rm_file(self, filepath):
        if os.path.isfile(filepath):
            os.remove(filepath)
            return True
        else:
            return False
    
    
    # copy file
    def cp_file(self, filepath, new_filepath):
        if shutil.copyfile(filepath, new_filepath):
            return True
    
    
    
    # deletes a directory. be careful!
    def rm_dir(self, dir):
        if os.path.isdir(dir) == True:
            shutil.rmtree(dir)
    
    
    
    # list directories
    def ls_dir(self, dir):
        if os.path.isdir(dir) == True:
            return os.listdir(dir)