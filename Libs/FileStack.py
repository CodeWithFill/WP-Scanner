# IMPORT LIBRARIES
import os
from pathlib import Path
import re
import shutil
#import scandir


class FileStack:

    def makeDir(self, dirpath):
        if os.path.isdir(dirpath) == False:
            os.mkdir(dirpath)



    # is file
    def isFile(self, filepath):
        if os.path.isfile(filepath):
            return True
        return False


    # is directory
    def isDir(self, dirpath):
        if os.path.isdir(dirpath):
            return True
        return False



    # touch file
    def touch(self, filepath):
        if os.path.isfile(filepath) == False:
            _file = open(filepath, 'w+')
            _file.write('')
            _file.close()
            return True
        return False



    # get file size
    def filesize(self, filepath):
        return os.path.getsize(filepath)



    # replaces text in file
    def fileFindReplace(self, file_in, file_out, dicts):
        if len(dicts) > 0:
            # read file_in, create and open file_out
            data = open(file_in).read().decode('ascii', 'ignore')
            new_file = open(file_out, 'w')

            for dict in dicts:
                for key in dict:
                    data = re.sub(key,dict[key], data)

            # write and close new file
            new_file.write(data)
            new_file.close()


    def lsDirDeep(self, path=None, chunks=False):
        if path == None or self.isDir(path) == False:
            return False

        fileList = []

        #for root, subFolders, files in scandir.walk(path):
        for root, subFolders, files in os.walk(path):
            for _file in files:
                fileList.append(os.path.join(root,_file))

        if fileList:
            if chunks != False:
                return self.__chunks(fileList, chunks)
            return fileList

        return False


    def __chunks(self, l, n):
        _list = []
        for i in xrange(0, len(l), n):
            _list.append(l[i:i+n])
        return _list






    # delete file
    def removeFile(self, filepath):
        if os.path.isfile(filepath):
            os.remove(filepath)
            return True
        else:
            return False


    # copy file
    def copyFile(self, filepath, new_filepath):
        if shutil.copyfile(filepath, new_filepath):
            return True



    # deletes a directory. be careful!
    def removeDir(self, dirpath):
        if os.path.isdir(dirpath) == True:
            shutil.rmtree(dirpath)


    # rename directory
    def renameDir(self, dirpath, dirNewName):
        if os.path.isdir(dirpath) == True:
            currentDir = Path(dirpath)
            currentDir.rename(dirNewName)



    # list directories
    def lsDir(self, dir):
        if os.path.isdir(dirpath) == True:
            return os.listdir(dirpath)
