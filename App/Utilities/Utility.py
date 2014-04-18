# IMPORT LIBRARIES
from time import gmtime, strftime


class Utility:
    
    # return timestamp
    def timestamp(self, day = False):
        if day == False:
            format = "%Y-%m-%d %H:%M:%S +0000"
        else:
            format = "%Y-%m-%d"
        return strftime(format, gmtime())
    
    
    
    # if int return, if not return None
    def get_int(self, chk):
        if chk.isdigit():
            return int(chk)
        else:
            return None