# IMPORT LIBRARIES
import os
from boto.s3.connection import S3Connection

class S3:
    access = None
    secret = None
    bucket = None

    Conn = None
    Bucket = None

    # store url and token as variables in this class
    def __init__(self, access=None, secret=None):
        self.access = access
        self.secret = secret


    def connect(self, _bucket=None):
        if _bucket == None:
            return False

        self.bucket = _bucket
        self.Conn = S3Connection(self.access, self.secret)
        self.Bucket = self.Conn.get_bucket(self.bucket)
        return True


    def upload(self, filein=None, fileout=None):
        if filein == None or filein == False:
            return False

        if fileout == None:
            fileout = os.path.basename(filein)

        if self.Conn == None or self.Bucket == False:
            return False
        
        # delete existing file of same name
        try:
            self.Bucket.delete_key(fileout)
        except:
            return filein + ' | Could not delete key in bucket: ' + fileout

        # upload file
        try:
            key = self.Bucket.new_key(fileout)
            #key.set_metadata('Content-Disposition', 'attachment')
            key.set_contents_from_filename(filein)
        except:
            return filein + ' | Could not upload file to bucket: ' + fileout

        return None


    def size(self, key=None):
        if self.Bucket == None or key == None:
            return False

        key = self.Bucket.lookup(key)
        
        try:
            if key.size:
                return key.size
        except:
            return None

        return None

