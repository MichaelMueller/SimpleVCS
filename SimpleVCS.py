#!python3.6

import argparse
import os
import shutil
import sys
import traceback
import ctypes

# CONFIG
magicArchiveDir = ".__archive__"
FILE_ATTRIBUTE_HIDDEN = 0x02

# FUNCTIONS
def commit(leftDir, rightDir, currSubDir):
	# get all files on Left side
	currLeftSubDir = os.path.join(leftDir, currSubDir)
	filesLeft = []
	filesLeft = os.listdir(currLeftSubDir)
		
	# get all files on Right side
	currRightSubDir = os.path.join(rightDir, currSubDir)
	filesRight = []
	filesRight = os.listdir(currRightSubDir)
		
	# get differences
	filesAdded = list(set(filesLeft)-set(filesRight))
	filesRemoved = list(set(filesRight)-set(filesLeft))
	filesRemained = list(set(filesLeft) & set(filesRight))
	
	# add files
	for file in filesAdded:
		print ("Adding file %s" % os.path.join(currSubDir, file))		
		leftFile = os.path.join(currLeftSubDir, file)
		rightFile = os.path.join(currRightSubDir, file)
		if(os.path.isdir(leftFile)):
			shutil.copytree( leftFile, rightFile )
		else:
			shutil.copyfile( leftFile, rightFile )

	# remove (save) files
	archiveDir = os.path.join(currRightSubDir, magicArchiveDir)
	for file in filesRemoved:
		print ("Moving file %s to archive %s" % (os.path.join(currSubDir, file), archiveDir))	
		if(not os.path.exists(archiveDir)):
			os.makedirs(archiveDir)
			# For windows set file attribute.
			if os.name == 'nt':
				ret = ctypes.windll.kernel32.SetFileAttributesW(archiveDir, FILE_ATTRIBUTE_HIDDEN)
		shutil.move( os.path.join(currRightSubDir, file), os.path.join(archiveDir, file) )
	
# MAIN
try:

	parser = argparse.ArgumentParser(description='SimpleVCS - a simple file versioning and backup system')

	parser.add_argument("left", help="The source dir to sync")
	parser.add_argument("right", help="The target dir that maintains versions")

	args = parser.parse_args()
	left = args.left
	right = args.right

	if( not os.path.exists(left) ):
		raise Exception("Directory %s does not exist"%left)

	if( not os.path.exists(right) ):
		os.makedirs(right)
	
	commit(left, right, "")
	
	sys.exit(0)
except SystemExit:
	sys.exit(0)
except:
	print ("Unexpected error:", sys.exc_info()[0])
	print ("Trace:", traceback.format_exc())
	sys.exit(-1)