#!python3

# TODOs: Operate remotely (SCP, SSH, etc.), STORE VERSIONS IN ZIP FILES, MORE TESTS
import argparse
import os
import shutil
import sys
import traceback
import ctypes
import hashlib
import fnmatch

# CONFIG (SHOULD BE PARAMS)
USE_FILEMTIME = False
COMPARE_CONTENTS = False
IGNORE_LIST = [".git", ".svn"]

# INTERNAL CONFIG
ARCHIVE_DIRNAME = ".__archive__"
TRAILING_ZEROS = 7
FILE_ATTRIBUTE_HIDDEN = 0x02
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

# FUNCTIONS
def getArchiveFileName(archiveDir, baseFileName):
	if(not os.path.exists(archiveDir)):
		os.makedirs(archiveDir)
		# For windows set file attribute.
		if os.name == 'nt':
			ret = ctypes.windll.kernel32.SetFileAttributesW(archiveDir, FILE_ATTRIBUTE_HIDDEN)
			
	archiveFileName = None
	i = 0
	while(archiveFileName == None or os.path.exists(os.path.join(archiveDir, archiveFileName))):
		i = i+1
		trailingPart = str(i)
		while( len(trailingPart) < TRAILING_ZEROS ):
			trailingPart = "0"+trailingPart
		fileParts = os.path.splitext(baseFileName)
		archiveFileName = fileParts[0] + trailingPart + fileParts[1]
	
	return os.path.join(archiveDir, archiveFileName)

def getHash(fileName):
	return hashlib.md5(open(fileName,'rb').read()).hexdigest()

def commit(leftDir, rightDir, currSubDir):
	# print ("Investigating and commiting the directory %s" % currSubDir)
	# get all files on Left side
	currLeftSubDir = os.path.join(leftDir, currSubDir)
	filesLeft = []
	filesLeft = os.listdir(currLeftSubDir)
	filesLeftClean = []
	for file in filesLeft:
		take = True
		for pattern in IGNORE_LIST:
			if fnmatch.fnmatch(file, pattern):
				print ("Ignoring file %s due to exclude list" % (os.path.join(currLeftSubDir, file)))
				take = False
		if(take):
			filesLeftClean.append(file)
	filesLeft = filesLeftClean
		
	# get all files on Right side
	currRightSubDir = os.path.join(rightDir, currSubDir)
	filesRight = []
	filesRight = os.listdir(currRightSubDir)
	# clean filesRight (archiveDir !!!)
	filesRightClean = []
	for file in filesRight:
		if(file != ARCHIVE_DIRNAME):
			filesRightClean.append(file)
	filesRight = filesRightClean
		
	# get differences
	filesAdded = list(set(filesLeft)-set(filesRight))
	filesRemoved = list(set(filesRight)-set(filesLeft))	
	filesRemained = list(set(filesLeft) & set(filesRight))
	
	# add files
	for file in filesAdded:
		leftFile = os.path.join(currLeftSubDir, file)
		rightFile = os.path.join(currRightSubDir, file)
		if(os.path.isdir(leftFile)):			
			print ("Creating added directory from %s to %s" % (leftFile, rightFile))
			os.makedirs(rightFile)
			commit(leftDir, rightDir, currSubDir + "/" + file)
		else:
			print ("Copy added file from %s to %s" % (leftFile, rightFile))	
			shutil.copy2( leftFile, rightFile )

	# remove (save) files
	archiveDir = os.path.join(currRightSubDir, ARCHIVE_DIRNAME)
	for file in filesRemoved:
		archiveFileName = getArchiveFileName(archiveDir, file)
		fileToBeMoved = os.path.join(currRightSubDir, file)
		print ("Moving deleted file from %s to %s" % (fileToBeMoved, archiveFileName))	
		shutil.move( fileToBeMoved, archiveFileName )
	
	# handle remained files
	for file in filesRemained:
	
		leftFile = os.path.join(currLeftSubDir, file)
		rightFile = os.path.join(currRightSubDir, file)
		
		# if we have dirs call this func recursively
		if(os.path.isdir(leftFile)):
			commit(leftDir, rightDir, currSubDir + "/" + file)
		# check file for similarity
		else:			
			statinfoLeft = os.stat(leftFile)
			statinfoRight= os.stat(rightFile)
			equals = True
			if( COMPARE_CONTENTS ):
				equals = getHash(leftFile) == getHash(rightFile)				
			else:
				equals = statinfoLeft.st_size == statinfoRight.st_size
				if( USE_FILEMTIME ):
					equals = equals and ( statinfoLeft.st_mtime == statinfoRight.st_mtime )
					
			# if they are not equals: move the old file to the archive
			if(not equals):
				archiveFileName = getArchiveFileName(archiveDir, file)
				print ("Moving changed file from %s to %s" % (os.path.join(currSubDir, file), archiveFileName))	
				shutil.move( rightFile, archiveFileName )
				print ("Copying modified file from %s to %s" % (leftFile, rightFile))
				shutil.copy2( leftFile, rightFile )
# MAIN
try:

	parser = argparse.ArgumentParser(description='SimpleVCS - a simple file versioning and backup system')

	parser.add_argument("LEFTDIR", help="The source dir to sync")
	parser.add_argument("RIGHTDIR", help="The target dir that maintains versions")
	parser.add_argument('--filemtime', dest='filemtime', action='store_true', default=USE_FILEMTIME, help='Turn on to use modified time for file comparison in addition to the filesize')
	parser.add_argument('--contents', dest='contents', action='store_true', default=COMPARE_CONTENTS, help='Turn on to use the calculation of hashes for file comparison. This will replace using filesize and modified time')
	parser.add_argument('--ignore', dest='ignore', action='append', default=IGNORE_LIST, help='Specify unix file expressions that should be excluded')

	args = parser.parse_args()
	left = args.LEFTDIR
	right = args.RIGHTDIR
	USE_FILEMTIME = args.filemtime
	COMPARE_CONTENTS = args.contents
	IGNORE_LIST = args.ignore
	
	print("")
	print("Running SimpleVCS with the following options:")
	print("%s" %(str(args)))
	print("*******************************")

	if( not os.path.exists(left) ):
		raise Exception("Directory %s does not exist"%left)

	if( not os.path.exists(right) ):
		os.makedirs(right)
	
	commit(left, right, ".")
	
	sys.exit(0)
except SystemExit:
	sys.exit(0)
except:
	print ("Unexpected error:", sys.exc_info()[0])
	print ("Trace:", traceback.format_exc())
	sys.exit(-1)