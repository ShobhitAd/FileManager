# File Manager
# Author : Shobhit Adlakha

import hashlib, os, sys;

class FileManager():
    def __init__(self, ext):
        self.EXT = []
        self.SEARCH_SUBDIRS = True

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
            return True;
        for ext in self.EXT:
            if file.endswith('.' + ext.lower()):
                return True;
        return False;

    def log_load(self, file_name = 'files', curDir = os.getcwd()):
        data = {}
        file_path = os.path.join(curDir, file_name + '.log')
        log_file = open(file_path, 'r')

        for line in log_file:
            f_name = line[:-1].split('\t')[0]
            f_hash = line[:-1].split('\t')[1]
            data[f_name] = f_hash

        log_file.close()
        return data;

    def log_update(self, file_name = 'files', curDir = os.getcwd()):
        file_path = os.path.join(curDir, file_name + '.log')
        log_file = open(file_path, 'w')
        file_list = self.getFileList()
        for file in file_list:
            log_file.write(file + '\t' + hash(file) + '\n')
        log_file.close()



    def log_compare(self, log_data, file_list):
        newFile_list = []
        delFile_list = []
        modFile_list = []
        rnmFile_list = []

        for file in file_list:
            if file in log_data.keys():
                if hash(file) != log_data[file]: # Modified file
                    modFile_list.append(file)
            else:
                if hash(file) in log_data.values(): # Renamed file
                    rnmFile_list.append(file)
                else: # New file
                    newFile_list.append(file)

        for file in log_data.keys():
            if file not in file_list and file not in modFile_list and file not in rnmFile_list: # Deleted file
                delFile_list.append(file)

        return newFile_list, delFile_list, modFile_list, rnmFile_list;

def hash(file_path):
    f = open(file_path, 'rb')
    readFile = f.read()
    hash_func = hashlib.md5(readFile)

    return hash_func.hexdigest();

def printComparison(title, lst):
    print(title)

    if len(lst) == 0:
        print('\t No entries')
    for file in lst:
        print('\t' + file)

if __name__ == '__main__':
    print(' Welcome to File Manager. Enter your command\n')

    fm = FileManager(list(sys.argv[1:]))

    while True:
        command = input('>>')
        command = command.lower().split(" ")

        if command[0] == 'quit' or command[0] == 'q': # Exit program
            print('Thanks for using File Manager.')
            sys.exit(0)
        elif command[0] == 'log': # Write file and hash list to log file
            fm.log_update()
        elif command[0] == 'compare': # Compare log file and actual files
            log_data = fm.log_load()
            file_list = fm.getFileList()

            n, d, m, r = fm.log_compare(log_data, file_list)

            print('Comparison results....')
            printComparison('NEW:', n)
            printComparison('DELETE:', d)
            printComparison('MODIFIED:', m)
            printComparison('RENAMED:', r)


        else:
            print('Invalid command')