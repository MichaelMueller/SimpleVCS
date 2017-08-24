#!python3

import argparse
import os
import sys
import traceback
import string
import random
import shutil
import hashlib

# FUNCTIONS
def getHash(fileName):
	return hashlib.md5(open(fileName,'rb').read()).hexdigest()
	
def writeFile(fileName, data):
    with open(fileName, 'w') as x_file:
        x_file.write(data)

def randomString(size=100, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
	
# MAIN
try:

	parser = argparse.ArgumentParser(description='SimpleVCSTest - a test program for SimpleVCS')
	parser.add_argument("workingdir", help="The working dir for the test")
	args = parser.parse_args()
	workingdir = args.workingdir
	print("workingdir is %s" % workingdir)

	# create test dir left
	leftDirName = "left"
	leftDir = os.path.join(workingdir, leftDirName)
	if(os.path.exists(leftDir)):
		shutil.rmtree(leftDir)
	os.makedirs(leftDir)
	leftDirs = ["sub1", "sub1/subsub1", "sub2", "sub2/.git", ".svn"]
	for dir in leftDirs:
		fullPath = os.path.join(leftDir, dir)
		if( not os.path.exists(fullPath) ):
			print( "creating dir %s" % dir )
			os.makedirs( fullPath )
	
	# create files
	leftFiles = [ "file_1.txt", "sub1/file_2.txt", "sub1/file_3", "sub1/subsub1/file_4.txt" ]
	for leftFile in leftFiles:
		print( "creating file %s" % leftFile )
		writeFile( os.path.join(leftDir, leftFile), randomString() )
	
	# initial sync check if everythin is there
	rightDir = os.path.join(workingdir, "right")
	if(os.path.exists(rightDir)):
		shutil.rmtree(rightDir)
	os.system("SimpleVCS.py %s %s" % (leftDir, rightDir))
	
	# sparse checks
	hashLeft = getHash( os.path.join( leftDir, leftFiles[0] ) )
	hashRight = getHash( os.path.join( rightDir, leftFiles[0] ) )
	if( hashLeft != hashRight):
		raise Exception("Mismatching hashes for file %s. Please check initial copy" % (leftFiles[0]))
	
	print ("ALL TESTS PASSED")
	sys.exit(0)
except SystemExit:
	sys.exit(0)
except:
	print ("Unexpected error:", sys.exc_info()[0])
	print ("Trace:", traceback.format_exc())
	sys.exit(-1)
	