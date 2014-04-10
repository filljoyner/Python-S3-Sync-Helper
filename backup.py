# ==============================================================================
# Python S3 Sync Helper
# ------------------------------------------------------------------------------
# Written Hastily by:	Philip Joyner
# Version:				0.1
# Last Updated:			2014-04-09
# Python Version:		2.7
# Requirements:			Python 2.7 & Boto
# ------------------------------------------------------------------------------


# import libs
import os
import sys
from time import gmtime, strftime
sys.path.append(os.getcwd() + "\\Utilities")

from FileStack import FileStack
from S3 import S3
from config import Config

# assign configuration details (info from config.py)
access = Config['s3_access']
secret = Config['s3_secret']
bucket = Config['s3_bucket']
basefolder = Config['s3_folder']
workspace = Config['local_dir']
basename = os.path.basename(workspace)

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
FS = FileStack()
s3 = S3(access, secret)

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
files = FS.folder_read(workspace)

# initialize some stuff
time_format = "%Y-%m-%d %H:%M:%S +0000"
start_time = strftime(time_format, gmtime())
file_num = 0
upload_num = 0
present_num = 0
updated_num = 0
empty_num = 0
file_count = 0




# if files are returned
if files:
	file_num = len(files)
	file_pad = len(str(file_num))

	print '-----------------------------------------------------'
	print 'Processing ' + str(file_num) + ' file(s)'
	print '-----------------------------------------------------'
	print ''

	# connect to bucket
	if s3.connect(bucket):
		# cycle through files and do the do
		for _file in files:
			s3_file = file_prefix + '/' + _file[len(workspace)+1:].replace('\\', '/')
			s3_file_show = '...' + s3_file[-40:]

			local_filesize = FS.filesize(_file)
			s3_filesize = s3.size(s3_file)

			# if local filesize is more than 0
			if local_filesize:
				# if s3_filesize is not present (key not used), upload file
				if s3_filesize == None:
					s3.upload(_file, s3_file)
					upload_num += 1
					file_count+= 1
					print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Upload: ' + s3_file_show

				# if local filesize is not the same as s3 filesize, upload file
				elif local_filesize != s3_filesize:
					s3.upload(_file, s3_file)
					updated_num += 1
					file_count+= 1
					print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Local != S3 - Upload: ' + s3_file_show

				# if local filesize and s3 filesize are the same, file must be same
				elif local_filesize == s3_filesize:
					present_num += 1
					file_count+= 1
					print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Present (' + str(local_filesize) + '==' + str(s3_filesize) + '): ' + s3_file_show

			# give local file size is 0 error
			else:
				empty_num+= 1
				file_count+= 1
				print str(file_count).rjust(file_pad) + '/' + str(file_num) + ' | Local size 0: ' + s3_file_show
	# give bucket connection error
	else:
		print 'S3 Connection Error: Check credentials, permissions and bucket name'



# figure out number display size for presentation... don't worry about this stuff
_found_num = str(file_num).rjust(file_pad)
_upload_num = str(upload_num).rjust(file_pad)
_present_num = str(present_num).rjust(file_pad)
_updated_num = str(updated_num).rjust(file_pad)
_empty_num = str(empty_num).rjust(file_pad)
_total_num = str(upload_num + present_num + updated_num + empty_num).rjust(file_pad)

print ''
print '-----------------------------------------------------'
print 'Details - ' + _found_num +   '/' + _total_num + ' Processed'
print '-----------------------------------------------------'
print _upload_num +  ' file(s) Uploaded       (New)'
print _present_num + ' file(s) Present in S3  (Exists)'
print _updated_num + ' file(s) Updated in S3  (Overwritten)'
print _empty_num +   ' file(s) Skipped        (0 byte)'
print ''
print ' Started: ' + str(start_time)
print 'Finished: ' + str(strftime(time_format, gmtime()))
