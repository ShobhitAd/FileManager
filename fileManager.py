# File Manager
# Author : Shobhit Adlakha
import hashlib, os, sys, shutil;
import pprint;

#-------------------------- Classes
class FileManager():
    def __init__(self, ext):
        # FileManager Options
        self.FILE_TYPE = []
        self.SEARCH_SUBDIRS = True

    def getDirList(self, curDir = os.getcwd()):
        dir_list = []
        # Find all subdirectories
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
            # Find all files
            for node in os.scandir(dir):
                if node.is_dir() and self.SEARCH_SUBDIRS:
                    dir_queue.append(node.path)
                elif node.is_file() and self.hasExtension(node.name.lower()):
                    file_list.append(node.path[len(curDir) + 1:])

        return file_list;

    def hasExtension(self, file):
        # All files
        if len(self.FILE_TYPE) == 0:
            return True;

        # Specific extensions being tracked
        for ft in self.FILE_TYPE:
            if file.endswith('.' + ft.lower()):
                return True;
        return False;

    def sync(self, src_dir, dest_dir):

        if not (os.path.isdir(src_dir) and os.path.isdir(dest_dir)):
            return False

        # Get file list of source directory
        srcFiles = self.getFileList(src_dir)

        # Log destination directory
        log_inst = Log('tmpSync', self)
        log_inst.update(dest_dir)
        dest_Data = log_inst.load(dest_dir)

        self.createMissingDirs(src_dir, dest_dir)

        # File operations
        n, d, m, r = log_inst.compare(dest_Data, srcFiles, src_dir)

        print('The following changes will be made\n')
        printComparison('Create:', n)
        printComparison('Replace:', m)
        printComparison('Rename:', r)
        printComparison('Delete:', d)

        confirmation = user_input('\nContinue with sync(yes/no): ', 'yes')
        if confirmation == 'yes':
            print('Starting sync')
        else:
            print('Sync cancelled')
            return False



        for file in (n + m): # New and modified files
            src = os.path.join(src_dir, file)
            dest = os.path.join(dest_dir, file)
            shutil.copy2(src, dest)

        for file in d: # Deleted files
            dest = os.path.join(dest_dir, file)
            os.remove(dest)

        ind = 0
        for path_pair in r: # Give files a temporary name to avoid conflicts
            src = os.path.join(dest_dir, path_pair[0])

            path_pair[0] = path_pair[0] + '0x00000000-' + str(ind)
            ind += 1
            dest = os.path.join(dest_dir, path_pair[0])
            os.rename(src, dest)

        for path_pair in r: # Rename the files correctly
            src = os.path.join(dest_dir, path_pair[0])
            dest = os.path.join(dest_dir, path_pair[1])
            os.rename(src, dest)

        # Delete temporary log files
        log_inst.delete()
        return True

    def createMissingDirs(self, src_dir, dest_dir):
        subdir_queue = [(src_dir, dest_dir)]

        while len(subdir_queue) > 0:
            parent_path = subdir_queue[0]
            dir_list = self.getDirList(parent_path[0])
            subdir_queue.pop(0)

            for dir in dir_list:
                src = os.path.join(parent_path[0], dir)
                dest = os.path.join(parent_path[1], dir)
                if not os.path.isdir(dest):
                    os.mkdir(dest)

                subdir_queue.append((src, dest))


class Log():

    def __init__(self, file_name, fm):
        self.FILE_NAME = file_name
        self.FM = fm
        self.FILE_TYPE = '.fmLog'

    def load(self, curDir = os.getcwd()):
        data = {}
        file_path = os.path.join(curDir, self.FILE_NAME + self.FILE_TYPE)

        if not os.path.isfile(file_path):
            return None

        log_file = open(file_path, 'r')

        for line in log_file:
            f_name = line[:-1].split('\t')[0]
            f_hash = line[:-1].split('\t')[1]
            data[f_name] = f_hash

        log_file.close()
        return data;


    def update(self, curDir = os.getcwd()):
        file_path = os.path.join(curDir, self.FILE_NAME + self.FILE_TYPE)
        try:
            log_file = open(file_path, 'w')
            file_list = self.FM.getFileList(curDir)
            for file in file_list:
                log_file.write(file + '\t' + hash(file, curDir) + '\n')
            log_file.close()
            return True
        except:
            return False


    def compare(self, log_data, file_list, curDir = os.getcwd()):
        newFile_list = []
        delFile_list = []
        modFile_list = []
        rnmFile_list = []

        for file in file_list:
            if file in log_data.keys():
                if hash(file, curDir) != log_data[file]: # Modified file
                    modFile_list.append(file)
            else:
                if hash(file, curDir) in log_data.values(): # Renamed file
                    prev_name = list(log_data.keys())[list(log_data.values()).index(hash(file, curDir))]
                    rnmFile_list.append([prev_name, file])
                else: # New file
                    newFile_list.append(file)

        for file in log_data.keys():
            if file not in file_list and file not in modFile_list and file not in [r[0] for r in rnmFile_list]: # Deleted file
                delFile_list.append(file)

        return newFile_list, delFile_list, modFile_list, rnmFile_list;

    def delete(self, curDir = os.getcwd()):
        path = os.path.join(curDir, self.FILE_NAME + self.FILE_TYPE)
        if os.path.isfile(path):
            os.remove(path)
            return True;
        else:
            return False;



#-------------------------- Functions
def hash(file_path, curDir = os.getcwd()):
    file_path = os.path.join(curDir, file_path)
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

def user_input(msg, default = '', special = []):
    txt = input(msg)
    if txt.strip() == '': # No input
        txt = default
    for case in special:
        if txt.startswith(case[0]):
            txt = case[1] + txt[len(case[0]):]
    return txt;

#-------------------------- Main
if __name__ == '__main__':
    print(' Welcome to File Manager. Enter your command\n')

    fm = FileManager(list(sys.argv[1:]))

    while True:
        command = user_input('>>')
        command = command.lower().split(" ")

        if command[0] == 'quit' or command[0] == 'q': # Exit program
            print('Thanks for using File Manager.')
            sys.exit(0)

        elif command[0] == 'help' or command[0] == 'h': # Commands Reference
            print('Tracking extensions...' + str(fm.FILE_TYPE))
            print('Searching subdirs...' + str(fm.SEARCH_SUBDIRS))

            print('List of commands...')

            print('log:')
            print('\tCommit the changes to the log file')

            print('compare:')
            print('\tRun a comparison against the log to find which files are new, updated, deleted or renamed')

            print('sync:')
            print('\tSync the files between a source and destination directory')

            print('opt <var_name> val1[,val2]*:')
            print('\tUse opt to list and change file manager options')

            print('del:')
            print('\tDelete the existing log file')

            print('quit:')
            print('\tExit the program')


        elif command[0] == 'log': # Write file and hash list to log file
            log_name = user_input('\t Enter name of log file: ', 'files', [('~' , os.getcwd())])
            log_inst = Log(log_name, fm)
            if log_inst.update():
                print('Log updated')
            else:
                print('Failed Log update')

        elif command[0] == 'sync': # Sync files between a source and destination directory
            src = user_input('\tEnter Source directory(~ for referencing cwd): ', os.getcwd(), [('~' , os.getcwd())])
            dest = user_input('\tEnter Destination directory(~ for referencing cwd): ', os.getcwd(), [('~' , os.getcwd())])
            if fm.sync(src, dest):
                print('Successfully synced')
            else:
                print('Failed sync')


        elif command[0] == 'compare': # Compare log file and actual files
            log_name = user_input('\t Enter name of log file: ', 'files', [('~' , os.getcwd())])
            log_inst = Log(log_name, fm)
            log_data = log_inst.load()
            file_list = fm.getFileList()

            if log_data == None:
                print('Failed to load log data')
            else:
                n, d, m, r = log_inst.compare(log_data, file_list)

                print('Comparison results....')
                printComparison('NEW:', n)
                printComparison('DELETE:', d)
                printComparison('MODIFIED:', m)
                printComparison('RENAMED:', r)

        elif command[0] == 'del':
            log_name = user_input('\t Enter name of log file: ', 'files', [('~' , os.getcwd())])

            log_inst = Log(log_name, fm)
            if log_inst.delete():
                print('Log file deleted')
            else:
                print('Log file does not exist')

        elif command[0] == 'opt':
            if len(command) == 1:
                print('FILE_TYPE: ' + str(fm.FILE_TYPE))
                print('SEARCH_SUBDIRS: ' + str(fm.SEARCH_SUBDIRS))
            elif len(command) == 3:
                if command[1] == 'file_type':
                    fm.FILE_TYPE = command[2].split(',')
                    if fm.FILE_TYPE[0] == '' or fm.FILE_TYPE[0] == 'none':
                        fm.FILE_TYPE = []
                    print('FILE_TYPE: ' + str(fm.FILE_TYPE))
                elif command[1] == 'search_subdirs':
                    fm.SEARCH_SUBDIRS = (command[2] == 'true')
                    print('SEARCH_SUBDIRS: ' + str(fm.SEARCH_SUBDIRS))
            else:
                print('Invalid number of arguments')

        else:
            print('Invalid command')
