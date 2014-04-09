# ==============================================================================
# Python S3 Sync Helper
# ------------------------------------------------------------------------------
# Written Hastily by:	Philip Joyner
# Version:				0.1
# Last Updated:			2014-04-09
# Python Version:		2.7
# Requirements:			Python 2.7 & Boto
#
# ------------------------------------------------------------------------------
#
# INSTALLATION
#
# -----------------
#
# Python
# Download and install Python 2.7 - https://www.python.org/download/releases/2.7.6/
#
# pip:
# Install pip to install boto. Makes package installation a breeze
# http://www.pip-installer.org/en/latest/installing.html
#
# boto
# pip install boto
#
# ------------------------------------------------------------------------------
#
# HOW TO USE
# 
# -----------------
#
# Rename config.example.py to config.py
# The config file requires the following info
# 
# s3_access: api access key
#
# s3_secret: api secret
#
# s3_bucket: The bucket in s3 where your files will be uploaded
#
# s3_folder: Optional. The folder to upload the files to. If not set
#			 this will become the local_dir folder
#
# local_dir: The local directory you would like to upload files from
#
# ------------------------------------------------------------------------------
#
# WARNINGS / NOTES
# 
# -----------------
#
# Use at your own risk. If a key exists and a file is uploaded that key
# will be overwritten. Make sure the bucket "folder" you are uploading
# to is the one you would like to overwrite.
#
# Files that are in S3 that have been deleted locally will not be
# deleted. In this version S3 does not sync down first. This would be a
# good feature though.
#
# Might be nice to add a GUI too. One thing at a time.
#
# ==============================================================================


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
print '-----------------------------------------'
print 'Python S3 Upload Thingie!'
print '-----------------------------------------'
print ''
print 'local folder: ' + workspace
print '   s3 folder: ' + file_prefix
print ''
print '-----------------------------------------'
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




# if files are returned
if files:
	file_num = len(files)

	print '-----------------------------------------'
	print 'Processing ' + str(file_num) + ' file(s)'
	print '-----------------------------------------'
	print ''

	# connect to bucket
	if s3.connect(bucket):
		# cycle through files and do the do
		for _file in files:
			s3_file = file_prefix + '/' + _file[len(workspace)+1:].replace('\\', '/')
			local_filesize = FS.filesize(_file)
			s3_filesize = s3.size(s3_file)

			# if local filesize is more than 0
			if local_filesize:
				# if s3_filesize is not present (key not used), upload file
				if s3_filesize == None:
					s3.upload(_file, s3_file)
					upload_num += 1
					print 'Upload: ' + s3_file

				# if local filesize is not the same as s3 filesize, upload file
				elif local_filesize != s3_filesize:
					s3.upload(_file, s3_file)
					updated_num += 1
					print 'Local != S3 - Upload: ' + s3_file

				# if local filesize and s3 filesize are the same, file must be same
				elif local_filesize == s3_filesize:
					print 'Present: ' + s3_file
					present_num += 1


			# give local file size is 0 error
			else:
				print 'Local size 0: ' + s3_file
	# give bucket connection error
	else:
		print 'S3 Connection Error: Check credentials, permissions and bucket name'



# figure out number display size for presentation... don't worry about this stuff
_upload_num = str(upload_num)
_present_num = str(present_num)
_updated_num = str(updated_num)

display_size = len(_upload_num)

if len(_present_num) > display_size:
	display_size = len(_present_num)

if len(_updated_num) > display_size:
	display_size = len(_updated_num)

if len(_upload_num) < display_size:
	_upload_num = _upload_num.rjust(display_size)
if len(_present_num) < display_size:
	_present_num = _present_num.rjust(display_size)
if len(_updated_num) < display_size:
	_updated_num = _updated_num.rjust(display_size)

print ''
print '-----------------------------------------'
print ''
print _upload_num +  ' file(s) Uploaded       (New)'
print _present_num + ' file(s) Present in S3  (Exists)'
print _updated_num + ' file(s) Updated in S3  (Overwritten)'
print ''
print '-----------------------------------------'
print ''
print ' Started: ' + str(start_time)
print 'Finished: ' + str(strftime(time_format, gmtime()))
