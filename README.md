#Python S3 Upload Thingie
--

Written Hastily by:	Philip Joyner

Version: 0.1

Last Updated: 2014-04-09

Python Version: 2.7

Requirements: Python 2.7 & Boto

--

##INSTALLATION

-

Python - Download and install Python 2.7

https://www.python.org/download/releases/2.7.6/


pip - Install pip to install boto. Makes package installation a breeze

http://www.pip-installer.org/en/latest/installing.html

boto

pip install boto

--

##HOW TO USE

--

Rename config.example.py to config.py

```
Config = {
	's3_access' : 'YOUR ACCESS HERE',
	's3_secret' : 'YOUR SECRET HERE',
	's3_bucket' : 'YOUR BUCKET HERE',
	's3_folder' : None, 								# default is: None
	'local_dir' : 'C:/full/path/of/directory/to/upload' # use '/' in place of '\'
}
```

The config file requires the following info

s3_access: api access key

s3_secret: api secret

s3_bucket: The bucket in s3 where your files will be uploaded

s3_folder: Optional. The folder to upload the files to. If not set this will become the local_dir folder

local_dir: The local directory you would like to upload files from

------------------------------------------------------------------------------

##WARNINGS / NOTES

-----------------

Use at your own risk. If a key exists and a file is uploaded that key will be overwritten. Make sure the bucket "folder" you are uploading to is the one you would like to overwrite.

Files that are in S3 that have been deleted locally will not be deleted. In this version S3 does not sync down first. This would be a good feature though.

Might be nice to add a GUI too. One thing at a time.

==============================================================================