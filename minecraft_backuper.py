# Minecraft backup tool to dropbox
# NB! Need Dropbox.com account and enabled developer

# Run as cronjob once each day (Multiple runs will end in overwriting previous backup same day)


import sys
from datetime import date, timedelta
import zipfile, os

# Requirements:
# upload.py from https://github.com/trondkla/dropbox-simple-backuper, follow installations there
from upload import Uploader

APP_KEY, APP_SECRET = '', ''
lines = open('password.txt', 'rb').read().splitlines()
if len(lines) == 2:
    APP_KEY = lines[0]
    APP_SECRET = lines[1]

ACCESS_TYPE = 'app_folder'  # should be 'dropbox' or 'app_folder' as configured for your app

def get_file_name(file_path, file_number):
	if(file_number > 0):
		return file_path[0:len(file_path)-4]+"."+str(len(files_to_be_uploaded))+".zip"
	else:
		return file_path[0:len(file_path)-4]+".zip"



def main():

	days_to_backup = 3


	if len(sys.argv) == 1:
		print "usage: python %s /path/to/minecraft/world-directory number_of_days_with_backup\n       i.e. python %s minecraft/world 3\n       Outputs minecraft-backup-yyyy-mm-dd.zip" % (sys.argv[0], sys.argv[0])
		sys.exit(2)

	if len(sys.argv) == 3:
		days_to_backup = int(sys.argv[2])

	# Path to minecraft world directory
	world_directory = sys.argv[1]

	# Uploader from upload.py script
	uploader = Uploader(APP_KEY, APP_SECRET)
	

	current_date = date.today()
	file_path = "%s.zip" % current_date

	#Zip folder into yyyy-mm-dd-#.zip

	size_of_files = 0
	files_to_zip = []
	archive_nr = 0
	files_to_be_uploaded = []

	files = dirEntries(world_directory, True)
	for file in files:
		# dropbox has a 150 MB max-size on files
		if os.path.getsize(file) + size_of_files > 150000000:
			file_arch = get_file_name(file_path, len(files_to_be_uploaded))
			makeArchive(files_to_zip, file_arch)
			files_to_be_uploaded.append(file_arch)
			
			files_to_zip = []
			size_of_files = 0


		files_to_zip.append(file)
		size_of_files += os.path.getsize(file)
		
		
	#archive remaining files
	file_arch = get_file_name(file_path, len(files_to_be_uploaded))
	makeArchive(files_to_zip, file_arch)
	files_to_be_uploaded.append(file_arch)

	# Update todays backup
	for file in files_to_be_uploaded:
		uploader.upload(file, force=True, overwrite=True)
		
		#delete local zip
		os.remove(file)


	# Delete old backup
	delete_date = current_date - timedelta(days=days_to_backup)
	file_date = "%s" % delete_date
	print "Deleting old files with date: %s" % file_date

	files = uploader.search("", file_date)

	for file in files:
		uploader.delete(file['path'])
	

### From http://bytes.com/topic/python/answers/851018-how-zip-directory-python-using-zipfile 
def makeArchive(fileList, archive):
    """
    'fileList' is a list of file names - full path each name
    'archive' is the file name for the archive with a full path
    """
    try:
        a = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)
        for f in fileList:
            print "archiving file %s" % (f)
            a.write(f)
        a.close()
        return True
    except: return False
 
def dirEntries(dir_name, subdir, *args):
    '''Return a list of file names found in directory 'dir_name'
    If 'subdir' is True, recursively access subdirectories under 'dir_name'.
    Additional arguments, if any, are file extensions to match filenames. Matched
        file names are added to the list.
    If there are no additional arguments, all files found in the directory are
        added to the list.
    Example usage: fileList = dirEntries(r'H:\TEMP', False, 'txt', 'py')
        Only files with 'txt' and 'py' extensions will be added to the list.
    Example usage: fileList = dirEntries(r'H:\TEMP', True)
        All files and all the files in subdirectories under H:\TEMP will be added
        to the list.
    '''
    fileList = []
    for file in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file)
        if os.path.isfile(dirfile):
            if not args:
                fileList.append(dirfile)
            else:
                if os.path.splitext(dirfile)[1][1:] in args:
                    fileList.append(dirfile)
        # recursively access file names in subdirectories
        elif os.path.isdir(dirfile) and subdir:
            print "Accessing directory:", dirfile
            fileList.extend(dirEntries(dirfile, subdir, *args))
    return fileList

if __name__ == '__main__':
	main()
