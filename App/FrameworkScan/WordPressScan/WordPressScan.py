import os
import re
import urllib.request
from zipfile import ZipFile
import filecmp

from Libs.FileStack import FileStack

class WordPressScan:
    pathCache = None
    pathWPWorkingVersion = None
    pathWPRepoVersion = None

    fileVersion = 'wp-includes/version.php'
    urlReleaseArchive = 'https://wordpress.org/wordpress-####.zip'
    wordpressVersion = None

    scanDirs = ['wp-admin', 'wp-includes']
    scanFiles = ['index.php', 'wp-activate.php', 'wp-blog-header.php', 'wp-comments-post.php', 'wp-cron.php', 'wp-links-opml.php', 'wp-load.php', 'wp-mail.php', 'wp-settings.php', 'wp-signup.php', 'wp-trackback.php', 'xmlrpc.php', 'wp-content/index.php', 'wp-content/plugins/index.php', 'wp-content/themes/index.php']

    listSubDirs = []

    compareResults = {
        'siteOnly' : [],
        'repoOnly' : [],
        'altered' : []
    }



    def __init__(self, pathWordPress):
        self.pathCache = os.getcwd().replace('\\', '/') + '/App/FrameworkScan/WordPressScan/cache'
        self.pathWPWorkingVersion = pathWordPress
        self.fileStack = FileStack()


    # download repository and check against wordpress install
    def repo(self):
        self.wordpressVersion = self._getVersion()
        self.pathWPRepoVersion = self.cacheVersion(self.wordpressVersion)
        self._doVersionComparison()

        return self.compareResults



    # get version number from the wordpress install
    def _getVersion(self):
        with open(self.pathWPWorkingVersion + '/' + self.fileVersion) as readFile:
            for num, line in enumerate(readFile, 1):
                if '$wp_version' in line:
                    matches = re.findall(r'\'(.+?)\'', line)

                    if matches:
                        wpVersion = matches[0]

        return wpVersion



    # cache a wordpress version from release archive
    def cacheVersion(self, version):
        pathWordPress = self.pathCache + '/' + version
        urlDownload = self.urlReleaseArchive.replace('####', version)
        pathZipFile = self.pathCache + '/wordpress-' + version + '.zip'

        if self.fileStack.isDir(pathWordPress):
            return pathWordPress

        # reading and writing our zip file
        remoteData = urllib.request.urlopen(urlDownload)
        localFile = open(pathZipFile, 'wb')
        localFile.write(remoteData.read())

        zipFile = ZipFile(pathZipFile)
        zipFile.extractall(self.pathCache)
        zipFile.close()

        self.fileStack.renameDir(self.pathCache + '/wordpress', self.pathCache + '/' + version)

        return pathWordPress



    def _doVersionComparison(self):
        # get directories to compare
        for scanDir in self.scanDirs:
            pathRepoScanDir = self.pathWPRepoVersion + '/' + scanDir
            self.listSubDirs.append(pathRepoScanDir)

            for path, subdirs, files in os.walk(pathRepoScanDir):
                for subDir in subdirs:
                    subDirFix = path + '/' + subDir
                    self.listSubDirs.append(subDirFix.replace('\\', '/'))

        # do directory comparison
        for subdir in self.listSubDirs:
            pathCmpRepo = subdir
            pathCmpSite = self.pathWPWorkingVersion + pathCmpRepo.replace(self.pathWPRepoVersion, '')

            cmpResults = filecmp.dircmp(pathCmpRepo, pathCmpSite)

            for right_only in cmpResults.right_only:
                self.compareResults['siteOnly'].append(subdir.replace(self.pathWPRepoVersion, '') + '/' + right_only)

            for left_only in cmpResults.left_only:
                self.compareResults['repoOnly'].append(subdir.replace(self.pathWPRepoVersion, '') + '/' + left_only)

            for diff_file in cmpResults.diff_files:
                self.compareResults['altered'].append(subdir.replace(self.pathWPRepoVersion, '') + '/' + diff_file)

        # do file comparisons
        fileCompareResult = filecmp.cmpfiles(self.pathWPRepoVersion, self.pathWPWorkingVersion, self.scanFiles, False)

        for fileRepoOnly in fileCompareResult[2]:
            self.compareResults['repoOnly'].append('/' + fileRepoOnly)

        for fileAltered in fileCompareResult[1]:
            self.compareResults['altered'].append('/' + fileAltered)
