# File Manager
# Author : Shobhit Adlakha

import hashlib, os, sys;

class FileManager():
    def __init__(self, ext):
        self.EXT = []
        self.SEARCH_SUBDIRS = True
        self.HASHES = {}

    def getDirList(self, curDir = os.getcwd()):
        dir_list = ['< ~ >', '< .. >']
        for node in os.scandir(curDir):
            if node.is_dir():
                dir_list.append(node.name)

        return dir_list

    def getFileList(self, curDir = os.getcwd()):
        file_list = []
        dir_queue = [curDir]

        # Run until directory queue is empty
        while len(dir_queue) != 0:
            dir = dir_queue.pop(0)

            for node in os.scandir(dir):
                if node.is_dir() and self.SEARCH_SUBDIRS:
                    dir_queue.append(node.path)
                elif node.is_file() and self.hasExtension(node.name.lower()):
                    file_list.append(node.path[len(curDir) + 1:])

        return file_list;

    def hasExtension(self, file):
        if len(self.EXT) == 0:
            return True
        for ext in self.EXT:
            if file.endswith('.' + ext.lower()):
                return True
        return False

    def log_update(self, file_name = 'files'):
        log_file = open(file_name + '.log', 'w')
        file_list = self.getFileList()
        for file in file_list:
            log_file.write(file + '\t' + str(hash(file)) + '\n')
        log_file.close()

    def hash(file_path):
        f = open(file_path, 'rb')
        readFile = f.read()
        hash_func = hashlib.md5(readFile)
        return hash_func.hexdigest();


if __name__ == '__main__':
    fm = FileManager([])
    print(fm.getFileList())
    print(fm.getDirList())
    fm.log_update()
