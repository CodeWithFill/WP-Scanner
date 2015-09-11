# importing functionality
import os
import re
import urllib.request
from zipfile import ZipFile
import filecmp
import sys

# importing custom classes
from Libs.FileStack import FileStack

# creating  app paths
pathApp = os.getcwd().replace('\\', '/')
pathWorkspace = pathApp + '/Workspace'
pathWordPress = pathApp + '/WordPress'

fileVersion = pathWorkspace + '/wp-includes/version.php'


# initialize variables
fileStack = FileStack()
wpVersion = False
scanDirs = ['wp-admin', 'wp-includes']
scanFiles = ['index.php', 'wp-activate.php', 'wp-blog-header.php', 'wp-comments-post.php', 'wp-cron.php', 'wp-links-opml.php', 'wp-load.php', 'wp-mail.php', 'wp-settings.php', 'wp-signup.php', 'wp-trackback.php', 'xmlrpc.php']

# dev speed
doDownload = doZip = doRename = True


# read wordpress version from wp file
with open(fileVersion) as readFile:
    for num, line in enumerate(readFile, 1):
        if '$wp_version' in line:
            matches = re.findall(r'\'(.+?)\'', line)

            if matches:
                wpVersion = matches[0]



if doDownload:
    # download remote and local paths
    urlDownload = 'https://wordpress.org/wordpress-' + wpVersion + '.zip'
    pathZipFile = pathWordPress + '/wordpress-' + wpVersion + '.zip'

    # reading and writing our zip file
    remoteData = urllib.request.urlopen(urlDownload)
    localFile = open(pathZipFile, 'wb')
    localFile.write(remoteData.read())


if doZip:
    # extracting zip file
    zipFile = ZipFile(pathZipFile)
    zipFile.extractall(pathWordPress)
    zipFile.close()


if doRename:
    # rename wordpress default folder to version folder
    fileStack.renameDir(pathWordPress + '/wordpress', pathWordPress + '/' + wpVersion)

    # zip file cleanup
    #fileStack.removeFile(pathZipFile)


# initialize variables for use with scanning and comparing
pathWPRepoVersion = pathWordPress + '/' + wpVersion

listSubDirs = []

compareResults = {
    'siteOnly' : [],
    'repoOnly' : [],
    'altered' : []
}


# build list of directories to scan
for scanDir in scanDirs:
    pathRepoScanDir = pathWPRepoVersion + '/' + scanDir
    listSubDirs.append(pathRepoScanDir)

    for path, subdirs, files in os.walk(pathRepoScanDir):
        for subDir in subdirs:
            subDirFix = path + '/' + subDir
            listSubDirs.append(subDirFix.replace('\\', '/'))



# handle directory comparisons against repo
for subdir in listSubDirs:
    pathCmpRepo = subdir
    pathCmpSite = pathWorkspace + pathCmpRepo.replace(pathWPRepoVersion, '')

    cmpResults = filecmp.dircmp(pathCmpRepo, pathCmpSite)

    for right_only in cmpResults.right_only:
        compareResults['siteOnly'].append(subdir.replace(pathWPRepoVersion, '') + '/' + right_only)

    for left_only in cmpResults.left_only:
        compareResults['repoOnly'].append(subdir.replace(pathWPRepoVersion, '') + '/' + left_only)

    for diff_file in cmpResults.diff_files:
        compareResults['altered'].append(subdir.replace(pathWPRepoVersion, '') + '/' + diff_file)



# handle file comparisons
fileCompareResult = filecmp.cmpfiles(pathWPRepoVersion, pathWorkspace, scanFiles, False)

for fileRepoOnly in fileCompareResult[2]:
    compareResults['repoOnly'].append('/' + fileRepoOnly)

for fileAltered in fileCompareResult[1]:
    compareResults['altered'].append('/' + fileAltered)


# print results
print(compareResults)
